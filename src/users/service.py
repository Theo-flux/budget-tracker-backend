from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import User
from src.utils.validators import is_email


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

    async def update_user(self, user: User, user_data: dict, session: AsyncSession):
        allowed_fields = ["first_name", "last_name", "password"]

        for field in allowed_fields:
            value = user_data.get(field)
            if value is not None:
                setattr(user, field, value)

        await session.commit()
        await session.refresh(user)
        return user
