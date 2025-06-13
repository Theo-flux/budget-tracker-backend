from typing import Optional
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError, InvalidTokenError

from src.auth.authentication import Authentication


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

        token_data = Authentication().decode_token(token)

        self.verify_token_data(token_data)

        return token_data

    def verify_token_data(self, token_data) -> None:
        raise NotImplementedError("Please override this method in child classes.")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data):
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Provide an access token.",
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data):
        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Provide a refresh token.",
            )
