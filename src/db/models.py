import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Column, DateTime, Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(primary_key=True, default=None)
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, nullable=False, index=True, unique=True)
    first_name: str = Field(...)
    last_name: str = Field(...)
    email: EmailStr = Field(...)
    phone_number: str = Field(...)
    password: str = Field(...)
    avatar: Optional[str] = Field(default="")
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True)),
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True)),
        default_factory=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<User: {self.model_dump()}>"
