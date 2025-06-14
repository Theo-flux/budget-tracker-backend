from fastapi import FastAPI, status
from contextlib import asynccontextmanager

from src.db.main import init_db
from src.users.routers import user_router
from src.auth.routers import auth_router
from src.utils.exceptions import (
    AccessTokenRequired,
    InvalidToken,
    RefreshTokenRequired,
    UserEmailExists,
    UserNotFound,
    UserPhoneNumberExists,
    WrongCredentials,
    create_exception_handler,
)


@asynccontextmanager
async def life_span(app: FastAPI):
    print("Server started...")
    await init_db()
    yield
    print("Server stopped...")


version = "v1"

app = FastAPI(
    title="FastAPI Template",
    description="A template for my FASTAPI apps to make things very easy for me whenever I am starting a new project.",
    version=version,
    lifespan=life_span,
)


app.add_exception_handler(
    InvalidToken,
    create_exception_handler(
        status.HTTP_403_FORBIDDEN,
        {"message": "This token is invalid or expired. Pls get a new token."},
    ),
)
app.add_exception_handler(
    UserNotFound,
    create_exception_handler(
        status.HTTP_404_NOT_FOUND, {"message": "User doesn't exist."}
    ),
)
app.add_exception_handler(
    WrongCredentials,
    create_exception_handler(
        status.HTTP_404_NOT_FOUND, {"message": "Wrong email or password."}
    ),
)
app.add_exception_handler(
    UserPhoneNumberExists,
    create_exception_handler(
        status.HTTP_409_CONFLICT, {"message": "User with phone number already exist."}
    ),
)
app.add_exception_handler(
    UserEmailExists,
    create_exception_handler(
        status.HTTP_409_CONFLICT, {"message": "User with email already exist."}
    ),
)
app.add_exception_handler(
    AccessTokenRequired,
    create_exception_handler(
        status.HTTP_403_FORBIDDEN, {"message": "Provide an access token."}
    ),
)
app.add_exception_handler(
    RefreshTokenRequired,
    create_exception_handler(
        status.HTTP_403_FORBIDDEN, {"message": "Provide a refresh token."}
    ),
)

app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
app.include_router(user_router, prefix=f"/api/{version}/users", tags=["user"])
