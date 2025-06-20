from fastapi import status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette_context import context

from src.auth.schemas import LoginResModel, ResetPwdModel, TokenUserModel
from src.db.models import User
from src.db.redis import add_jti_to_block_list
from src.misc.schemas import ServerRespModel
from src.tasks.email_tasks import send_email_verification_task, send_password_reset_task
from src.users.schemas import CreateUserModel, LoginUserModel
from src.users.service import UserService
from src.utils.exceptions import InvalidLink, UserEmailExists, UserNotFound, UserPhoneNumberExists, WrongCredentials

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
                data=TokenUserModel.model_validate(user).model_dump(),
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

    async def resend_verify_token(self, email: str, session: AsyncSession):
        if email:
            user = await user_service.get_user_by_email(email=email, session=session)

            if not user:
                raise UserNotFound()

            if user.is_email_verified:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=ServerRespModel[bool](data=True, message="Account already verified").model_dump(),
                )

            send_email_verification_task.delay(email=user.get("email"), first_name=user.get("first_name"))

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ServerRespModel[bool](data=True, message="Verification link sent!").model_dump(),
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ServerRespModel[bool](
                data=True, message="A Verification link will be sent if email exists in our data base."
            ).model_dump(),
        )

    async def verify_account(self, token: str, session: AsyncSession):
        token_data = Authentication.decode_url_safe_token(token=token)

        if token_data["email"]:
            email = token_data["email"]
            user = await user_service.get_user_by_email(email=email, session=session)

            if not user:
                raise UserNotFound()

            if user.is_email_verified:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=ServerRespModel[bool](data=True, message="Account already verified").model_dump(),
                )

            await user_service.update_user(user=user, user_data={"is_email_verified": True}, session=session)

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ServerRespModel[bool](data=True, message="Account verification successful.").model_dump(),
            )

        raise InvalidLink()

    async def forgot_pwd(self, email: str, session: AsyncSession):
        user = await user_service.get_user_by_email(email=email, session=session)

        if not user:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ServerRespModel[bool](
                    data=True, message="A password reset link will be sent to this email if it exists in our database."
                ).model_dump(),
            )

        if user.is_email_verified:
            send_password_reset_task.delay(email=user.email, first_name=user.first_name)

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ServerRespModel[bool](
                    data=True, message="A password reset link will be sent to this email if it exists in our database."
                ).model_dump(),
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ServerRespModel[bool](data=True, message="Account needs to be verified.").model_dump(),
        )

    async def update_pwd(self, token: str, data: ResetPwdModel, session: AsyncSession):
        token_data = Authentication.decode_url_safe_token(token=token)

        if token_data:
            email = token_data["email"]
            user = await user_service.get_user_by_email(email=email, session=session)

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

        raise InvalidLink()

    async def login_user(self, login_data: LoginUserModel, session: AsyncSession):
        user = await user_service.get_user_by_email(login_data.email, session)

        if user is None:
            raise UserNotFound()

        if Authentication.verify_password(login_data.password, user.password):
            user_data = TokenUserModel.model_validate(user)

            if user_data.is_email_verified:
                access_token = Authentication.create_token(user_data)
                refresh_token = Authentication.create_token(user_data=user_data, refresh=True)

                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=ServerRespModel[LoginResModel](
                        data={
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                            "is_email_verified": user_data.is_email_verified,
                            "is_phone_number_verified": user_data.is_phone_number_verified,
                        },
                        message="user token generated.",
                    ).model_dump(),
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ServerRespModel[LoginResModel](
                    data={
                        "access_token": "",
                        "refresh_token": "",
                        "is_email_verified": user_data.is_email_verified,
                        "is_phone_number_verified": user_data.is_phone_number_verified,
                    },
                    message="user account not verified.",
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

        send_email_verification_task.delay(
            email=user.get("email"), first_name=user.get("first_name"), base_url=context.get("base_url")
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ServerRespModel[bool](
                data=True, message="Account created! A mail has been sent to your inbox for verification."
            ).model_dump(),
        )
