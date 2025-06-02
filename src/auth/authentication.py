from fastapi import Depends
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import uuid
import logging

from config import Config


class Authentication:
    password_context = CryptContext(schemes=["bcrypt"])
    ACCESS_TOKEN_EXPIRY = 84000
    PWD_RESET_TOKEN_EXPIRY = 3600

    @staticmethod
    def generate_password_hash(password: str) -> str:
        return Authentication.password_context.hash(password)

    @staticmethod
    def verify_password(hash: str, password: str) -> bool:
        return Authentication.password_context.verify(password, hash)

    @staticmethod
    def create_token(user_data: dict, expiry: timedelta = None, refresh: bool = False):
        payload = {}

        payload["user"] = user_data
        payload["exp"] = datetime.now() + (
            expiry
            if expiry is not None
            else timedelta(seconds=Authentication.ACCESS_TOKEN_EXPIRY)
        )
        payload["jti"] = str(uuid.uuid4())
        payload["refresh"] = refresh
        token = jwt.encode(
            payload=payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM
        )

        return token

    @staticmethod
    def decode_token(token: str):
        try:
            token_data = jwt.decode(
                jwt=token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
            )

            return token_data
        except jwt.PyJWTError as e:
            logging.exception(e)
            raise None
