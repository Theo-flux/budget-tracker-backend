from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.authentication import Authentication
from src.auth.schemas import LoginResModel, TokenUserModel
from src.db.models import User
from src.misc.schemas import EmailTypes, ServerErrorModel, ServerRespModel
from src.utils.exceptions import UserEmailExists, UserNotFound, UserPhoneNumberExists, WrongCredentials
from src.utils.mail import create_message, mail
from src.utils.validators import is_email

from .schemas import CreateUserModel, LoginUserModel


class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email.lower())
        result = await session.exec(statement=statement)
        user = result.first()

        return user

    async def get_user_by_phone(self, phone_number: str, session: AsyncSession):
        statement = select(User).where(User.phone_number == phone_number)
        result = await session.exec(statement)
        user = result.first()

        return user

    async def user_exists(self, email_or_phone: str, session: AsyncSession):
        user = (
            self.get_user_by_email(email_or_phone, session)
            if is_email(email_or_phone)
            else self.get_user_by_phone(email_or_phone, session)
        )

        return False if user is None else True

    async def login_user(self, login_data: LoginUserModel, session: AsyncSession):
        if not login_data.password or not login_data.password.strip() or not login_data.email.strip():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ServerErrorModel[str](
                    error="provide an email/password pls.",
                    message="provide an email/password pls.",
                ).model_dump(),
            )

        user = await self.get_user_by_email(login_data.email, session)

        if user is None:
            raise UserNotFound()

        if Authentication.verify_password(login_data.password, user.password):
            user_data = TokenUserModel.model_validate(user)
            access_token = Authentication.create_token(user_data)
            refresh_token = Authentication.create_token(user_data=user_data, refresh=True)

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ServerRespModel[LoginResModel](
                    data={
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "is_email_verified": user_data.is_email_verified,
                        "is_phone_number_verified": user_data.is_phone_number_verified,
                    },
                    message="user logged in successfully.",
                ).model_dump(),
            )

        raise WrongCredentials()

    async def create_user(self, user_data: CreateUserModel, session: AsyncSession):
        user = user_data.model_dump()

        if await self.get_user_by_email(user.get("email"), session):
            raise UserEmailExists()

        if await self.get_user_by_phone(user.get("phone_number"), session):
            raise UserPhoneNumberExists()

        user["password"] = Authentication.generate_password_hash(user["password"])
        new_user = User(**user)

        session.add(new_user)
        await session.commit()

        email_token = Authentication.create_url_safe_token({"email": user.get("email")})
        verification_url = f"http://localhost:8000/api/v1/auth/verify/{email_token}"

        message = create_message(
            recipients=[user.get("email")],
            subject=EmailTypes.EMAIL_VERIFICATION.subject,
            template_body={"first_name": user.get("first_name"), "verification_url": verification_url},
        )

        await mail.send_message(message=message, template_name=EmailTypes.EMAIL_VERIFICATION.template)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ServerRespModel[bool](
                data=True, message="Account created! A mail has been sent to your inbox for verification."
            ).model_dump(),
        )
