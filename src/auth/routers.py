from typing import List

from fastapi import APIRouter, Body, Depends, Query, status
from pydantic import EmailStr
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import AccessTokenBearer, RefreshTokenBearer
from src.auth.schemas import LoginResModel, TokenUserModel
from src.auth.service import AuthService
from src.db.main import get_session
from src.misc.schemas import ServerRespModel
from src.users.schemas import CreateUserModel, LoginUserModel
from src.users.service import UserService
from src.utils.mail import create_message, mail

auth_router = APIRouter()

auth_service = AuthService()
user_service = UserService()


@auth_router.post("/send-mail")
async def send_mail(recipients: List[EmailStr] = Body(...)):
    html = "<h1>Hello, world! from fastapi template.</h1>"

    message = create_message(recipients=recipients, subject="Sending a test mail", body=html)

    await mail.send_message(message=message)

    return {"message": "Email sent!"}


@auth_router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=ServerRespModel[LoginResModel],
)
async def login_user(login_data: LoginUserModel = Body(...), session: AsyncSession = Depends(get_session)):
    return await user_service.login_user(login_data, session)


@auth_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=ServerRespModel[bool],
)
async def register_user(user: CreateUserModel = Body(...), session: AsyncSession = Depends(get_session)):
    return await user_service.create_user(user, session)


@auth_router.get(
    "/profile",
    status_code=status.HTTP_200_OK,
    response_model=ServerRespModel[TokenUserModel],
)
async def get_current_user_profile(
    token_payload: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    return await auth_service.get_current_user(token_payload, session)


@auth_router.get("/logout")
async def revoke_user_token(token_payload: dict = Depends(AccessTokenBearer())):
    return await auth_service.revoke_token(token_payload)


@auth_router.get("/new-access-token", status_code=status.HTTP_200_OK, response_model=ServerRespModel)
async def get_new_user_access_token(
    token_payload: dict = Depends(RefreshTokenBearer()),
):
    return await auth_service.new_access_token(token_payload)


@auth_router.get("/verify/{token}")
async def verify_account(token: str, session: AsyncSession = Depends(get_session)):
    return await auth_service.verify_account(token=token, session=session)


@auth_router.post("/new-verify-token")
async def new_verify_token(email: str = Query(...), session: AsyncSession = Depends(get_session)):
    return await auth_service.new_verify_token(email=email, session=session)
