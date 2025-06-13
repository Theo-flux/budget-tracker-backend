from fastapi import APIRouter, Depends, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import TokenModel
from src.auth.service import AuthService
from src.users.service import UserService
from src.auth.dependencies import RefreshTokenBearer
from src.misc.schemas import ServerRespModel
from src.users.schemas import CreateUserModel
from src.database.main import get_session

auth_router = APIRouter(prefix="/auth", tags=["auth"])

auth_service = AuthService()
user_service = UserService()


@auth_router.post(
    "/login", status_code=status.HTTP_200_OK, response_model=ServerRespModel[TokenModel]
)
async def login():
    pass


@auth_router.get("/profile")
async def get_profile():
    pass


@auth_router.post("/register", response_model=ServerRespModel[bool])
async def register_user(
    user: CreateUserModel = Body(...), session: AsyncSession = Depends(get_session)
):
    return await user_service.create_user(user, session)


@auth_router.get("/new-access-token")
async def new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    pass
