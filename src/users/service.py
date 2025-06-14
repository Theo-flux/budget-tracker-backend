from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from src.auth.schemas import LoginResModel, TokenUserModel

from .models import User
from src.utils.validators import is_email
from .schemas import CreateUserModel, LoginUserModel
from src.misc.schemas import ServerErrorModel, ServerRespModel
from src.auth.authentication import Authentication

auth_handler = Authentication()


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
        if (
            not login_data.password
            or not login_data.password.strip()
            or not login_data.email.strip()
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ServerErrorModel[str](
                    error="provide an email/password pls.",
                    message="provide an email/password pls.",
                ).model_dump(),
            )

        user = await self.get_user_by_email(login_data.email, session)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ServerErrorModel[str](
                    error="user with email doesn't exist",
                    message="user with email doesn't exist",
                ).model_dump(),
            )

        if auth_handler.verify_password(login_data.password, user.password):
            user_data = TokenUserModel.model_validate(user)
            access_token = auth_handler.create_token(user_data)
            refresh_token = auth_handler.create_token(user_data=user_data, refresh=True)

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

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=ServerErrorModel[str](
                error="email or password is wrong",
                message="email or password is wrong",
            ).model_dump(),
        )

    async def create_user(self, user_data: CreateUserModel, session: AsyncSession):
        user = user_data.model_dump()

        if await self.get_user_by_email(user.get("email"), session):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=ServerErrorModel[str](
                    error="user with email already exist",
                    message="user with email already exist",
                ).model_dump(),
            )

        if await self.get_user_by_phone(user.get("phone_number"), session):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=ServerErrorModel[str](
                    error="user with phone number already exist",
                    message="user with phone number already exist",
                ).model_dump(),
            )

        user["password"] = Authentication().generate_password_hash(user["password"])
        new_user = User(**user)

        session.add(new_user)
        await session.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ServerRespModel[bool](
                data=True, message="user created successfully."
            ),
        )
