import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

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


class LoginResModel(TokenModel):
    is_email_verified: bool
    is_phone_number_verified: bool


class TokenUserModel(BaseModel):
    id: int
    uuid: uuid.UUID
    first_name: str
    last_name: str
    avatar: Optional[str]
    email: str
    phone_number: str
    is_email_verified: bool
    is_phone_number_verified: bool

    model_config = ConfigDict(from_attributes=True)
