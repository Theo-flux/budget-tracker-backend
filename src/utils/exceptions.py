from typing import Any, Callable, Dict

from fastapi import FastAPI, status
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


class ExpiredLink(AppException):
    """This handles expired password reset token"""

    pass


class InvalidLink(AppException):
    """This handles invalid password reset token"""

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


def register_exceptions(app: FastAPI):
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status.HTTP_403_FORBIDDEN,
            {"message": "This token is invalid or expired. Pls get a new token."},
        ),
    )
    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(status.HTTP_404_NOT_FOUND, {"message": "User doesn't exist."}),
    )
    app.add_exception_handler(
        WrongCredentials,
        create_exception_handler(status.HTTP_404_NOT_FOUND, {"message": "Wrong email or password."}),
    )
    app.add_exception_handler(
        UserPhoneNumberExists,
        create_exception_handler(status.HTTP_409_CONFLICT, {"message": "User with phone number already exist."}),
    )
    app.add_exception_handler(
        UserEmailExists,
        create_exception_handler(status.HTTP_409_CONFLICT, {"message": "User with email already exist."}),
    )
    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(status.HTTP_403_FORBIDDEN, {"message": "Provide an access token."}),
    )
    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(status.HTTP_403_FORBIDDEN, {"message": "Provide a refresh token."}),
    )
    app.add_exception_handler(
        ExpiredLink,
        create_exception_handler(status.HTTP_403_FORBIDDEN, {"message": "Link expired. get a new one"}),
    )
    app.add_exception_handler(
        InvalidLink,
        create_exception_handler(status.HTTP_403_FORBIDDEN, {"message": "Link is invalid. get a new one"}),
    )

    @app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
    async def internal_server_error(request: Request, exc):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "A 500 error exception occured!", "error_code": "InternalServerError"},
        )
