from fastapi import status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.schemas import TokenUserModel

from .authentication import Authentication
from src.misc.schemas import ServerRespModel
from src.db.redis import add_jti_to_block_list
from src.users.service import UserService

user_service = UserService()


class AuthService:
    async def get_current_user(token_payload: dict, session: AsyncSession):
        user_email = token_payload["user"]["email"]
        user = await user_service.get_user_by_email(user_email, session)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ServerRespModel[TokenUserModel](
                data=TokenUserModel.model_validate(user).model_dump(),
                message="user profile retrieved",
            ),
        )

    async def revoke_token(self, token_payload: dict):
        jti = token_payload["jti"]
        await add_jti_to_block_list(jti)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ServerRespModel(
                data=True,
                message="logged out successfully.",
            ),
        )

    async def new_access_token(self, token_payload: dict):
        new_access_token = Authentication().create_token(token_payload["user"])
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ServerRespModel(
                data={"access_token": new_access_token},
                message="new access token generated.",
            ),
        )
