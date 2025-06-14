from typing import Optional
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth.authentication import Authentication
from src.database.redis import token_in_block_list


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(
            auto_error=auto_error,
        )

    def is_token_valid(self, token: str) -> bool:
        try:
            token = Authentication().decode_token(token)
            return True
        except:
            return False

    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        cred = await super().__call__(request)
        token = cred.credentials

        if self.is_token_valid(token) is False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired token.",
            )

        token_payload = Authentication().decode_token(token)

        if token_in_block_list(token_payload["jti"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This token is invalid. Pls get a new token.",
            )

        self.verify_token_data(token_payload)

        return token_payload

    def verify_token_data(self, token_payload) -> None:
        raise NotImplementedError("Please override this method in child classes.")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_payload):
        if token_payload and token_payload["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Provide an access token.",
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_payload):
        if token_payload and not token_payload["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Provide a refresh token.",
            )
