from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from .models import User
from src.utils.validators import is_email
from .schemas import CreateUserModel
from src.misc.schemas import ServerErrorModel, ServerRespModel
from src.auth.authentication import Authentication


class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email.lower())
        result = await session.exec(statement)
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

    async def create_user(self, user_data: CreateUserModel, session: AsyncSession):
        user = user_data.model_dump()

        if await self.get_user_by_email(user.get("email"), session):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=ServerErrorModel[str](
                    error="user with email already exist",
                    message="user with email already exist",
                ),
            )

        if await self.get_user_by_phone(user.get("phone_number"), session):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=ServerErrorModel[str](
                    error="user with phone number already exist",
                    message="user with phone number already exist",
                ),
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
