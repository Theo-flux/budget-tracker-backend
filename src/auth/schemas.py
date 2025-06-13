from typing import Optional
from pydantic import BaseModel, field_validator
from datetime import datetime

from src.utils.validators import email_validator


class ForgotPwdModel(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        return email_validator(value)


class ResetPwdModel(BaseModel):
    password: str


class UserResponseModel(BaseModel):
    id: int
    name: str
    avatar: Optional[str]
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
