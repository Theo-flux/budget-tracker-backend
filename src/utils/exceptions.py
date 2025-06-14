from typing import Any, Callable, Dict
from fastapi.requests import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """The base class for handling exceptions around the app."""

    pass


class InvalidToken(AppException):
    """This handles user invalid token exceptions"""

    pass


class UserEmailExists(AppException):
    """This handles user email exists"""

    pass


class UserPhoneNumberExists(AppException):
    """This handles user email exists"""

    pass


class UserNotFound(AppException):
    """This handles no user."""

    pass


class WrongCredentials(AppException):
    """This handles wrong user email or password."""

    pass


class TokenExpired(AppException):
    """This handles expired user token."""

    pass


class AccessTokenRequired(AppException):
    """This handles expired user token."""

    pass


class RefreshTokenRequired(AppException):
    """This handles expired user token."""

    pass


def create_exception_handler(
    status_code: int, extra_content: Dict[str, Any] = None
) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(req: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={"error_code": exc.__class__.__name__, **extra_content},
        )

    return exception_handler
