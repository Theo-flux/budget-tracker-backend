from typing import Generic, TypeVar
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
    error: T
    message: str

    class Config:
        # This makes the model accept arbitrary types for the generic T
        arbitrary_types_allowed = True
