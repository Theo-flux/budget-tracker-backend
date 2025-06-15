from typing import Generic, List, TypeVar

from fastapi import UploadFile
from pydantic import BaseModel

T = TypeVar("T")


class ServerRespModel(BaseModel, Generic[T]):
    data: T
    message: str

    class Config:
        # This makes the model accept arbitrary types for the generic T
        arbitrary_types_allowed = True


# Pagination metadata model
class Pagination(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int


# Combined response model
class PaginatedResponse(BaseModel, Generic[T]):
    result: list[T]
    pagination: Pagination


class ServerErrorModel(BaseModel, Generic[T]):
    error_code: T
    message: str

    class Config:
        # This makes the model accept arbitrary types for the generic T
        arbitrary_types_allowed = True


class EmailType:
    def __init__(self, _subject: str, _template: str):
        self.subject = _subject
        self.template = _template


class EmailTypes:
    EMAIL_VERIFICATION = EmailType("Verify your account", "email_verification.html")
    PWD_RESET = EmailType("Password reset", "pwd_reset.html")


class EmailModel(BaseModel):
    subject: str
    reciepients: List[str]
    payload: dict
    template: str
    attachments: List[UploadFile] = ([],)
