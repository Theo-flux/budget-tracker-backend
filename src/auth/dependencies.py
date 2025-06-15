from typing import Optional

from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth.authentication import Authentication
from src.db.redis import token_in_block_list
from src.utils.exceptions import AccessTokenRequired, InvalidToken, RefreshTokenRequired


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(
            auto_error=auto_error,
        )

    def is_token_valid(self, token: str) -> bool:
        try:
            token = Authentication.decode_token(token)
            return True
        except Exception:
            return False

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        cred = await super().__call__(request)
        token = cred.credentials

        if self.is_token_valid(token) is False:
            raise InvalidToken()

        token_payload = Authentication.decode_token(token)

        if await token_in_block_list(token_payload["jti"]):
            raise InvalidToken()

        self.verify_token_data(token_payload)

        return token_payload

    def verify_token_data(self, token_payload) -> None:
        raise NotImplementedError("Please override this method in child classes.")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_payload):
        if token_payload and token_payload["refresh"]:
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_payload):
        if token_payload and not token_payload["refresh"]:
            raise RefreshTokenRequired()
