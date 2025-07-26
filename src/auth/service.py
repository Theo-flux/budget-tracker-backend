from fastapi import status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.schemas import ChangePwdModel, TokenModel, TokenUserModel
from src.db.models import User
from src.db.redis import add_jti_to_block_list
from src.misc.schemas import ServerRespModel
from src.users.schemas import CreateUserModel, LoginUserModel
from src.users.service import UserService
from src.utils.exceptions import UserEmailExists, UserNotFound, UserPhoneNumberExists, WrongCredentials

from .authentication import Authentication

user_service = UserService()


class AuthService:
    async def get_current_user(self, token_payload: dict, session: AsyncSession):
        user_email = token_payload["user"]["email"]
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ServerRespModel[TokenUserModel](
                data=TokenUserModel.model_validate(
                    {
                        "id": user.id,
                        "uid": user.uid,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "avatar": user.avatar,
                        "email": user.email,
                        "phone_number": user.phone_number,
                    }
                ).model_dump(),
                message="user profile retrieved",
            ).model_dump(mode="json"),
        )

    async def revoke_token(self, token_payload: dict):
        jti = token_payload["jti"]
        await add_jti_to_block_list(jti)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ServerRespModel(
                data=True,
                message="logged out successfully.",
            ).model_dump(),
        )

    async def new_access_token(self, token_payload: dict):
        new_access_token = Authentication.create_token(TokenUserModel.model_validate(token_payload["user"]))
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ServerRespModel(
                data={"access_token": new_access_token},
                message="new access token generated.",
            ).model_dump(),
        )

    async def change_pwd(self, data: ChangePwdModel, session: AsyncSession):
        user = await user_service.get_user_by_email(email=data.email, session=session)

        if not user:
            raise UserNotFound()

        await user_service.update_user(
            user=user,
            user_data={"password": Authentication.generate_password_hash(data.model_dump().get("new_password"))},
            session=session,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ServerRespModel[bool](data=True, message="Password reset successful.").model_dump(),
        )

    async def login_user(self, login_data: LoginUserModel, session: AsyncSession):
        user = await user_service.get_user_by_email(login_data.email, session)

        if user is None:
            raise UserNotFound()

        if Authentication.verify_password(login_data.password, user.password):
            user_data = TokenUserModel.model_validate(
                {
                    "id": user.id,
                    "uid": user.uid,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "avatar": user.avatar,
                    "email": user.email,
                    "phone_number": user.phone_number,
                }
            )

            access_token = Authentication.create_token(user_data)
            refresh_token = Authentication.create_token(user_data=user_data, refresh=True)

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ServerRespModel[TokenModel](
                    data={
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    },
                    message="user token generated.",
                ).model_dump(),
            )

        raise WrongCredentials()

    async def create_user(self, user_data: CreateUserModel, session: AsyncSession):
        user = user_data.model_dump()

        if await user_service.get_user_by_email(user.get("email"), session):
            raise UserEmailExists()

        if await user_service.get_user_by_phone(user.get("phone_number"), session):
            raise UserPhoneNumberExists()

        user["password"] = Authentication.generate_password_hash(user["password"])
        new_user = User(**user)

        session.add(new_user)
        await session.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ServerRespModel[bool](data=True, message="Account created!").model_dump(),
        )
