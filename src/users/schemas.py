from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

from src.utils.validators import email_validator


class CreateUserModel(BaseModel):
    first_name: str = Field(...)
    last_name: str = Field(...)
    email: EmailStr = Field(...)
    phone_number: str = Field(...)
    password: str = Field(...)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        return email_validator(value)


class LoginUserModel(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        return email_validator(value)


class UserResponseModel(BaseModel):
    id: int
    name: str
    avatar: Optional[str]
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
