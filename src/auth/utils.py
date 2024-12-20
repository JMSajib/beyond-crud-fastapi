import logging
import uuid
from datetime import datetime, timedelta

import jwt
from jwt import ExpiredSignatureError, InvalidSignatureError
from passlib.context import CryptContext

from src.config import Config

ACCESS_TOKEN_EXPIRY = 3600

password_context = CryptContext(schemes=['bcrypt'])


def generate_password_hash(password: str) -> str:
    hash = password_context.hash(password)
    return hash


def verify_password(password: str, hash: str) -> bool:
    return password_context.verify(password, hash)


def create_access_token(
    user_data: dict, expiry: timedelta = None, refresh: bool = False
):
    payload = {}

    payload['user'] = user_data
    payload['exp'] = datetime.now() + (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    )
    payload['jti'] = str(uuid.uuid4)
    payload['refresh'] = refresh

    token = jwt.encode(
        payload=payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM
    )
    return token


def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
        )

        return token_data

    except ExpiredSignatureError:
        logging.error("Token has expired")
        return None

    except InvalidSignatureError:
        logging.error("Token signature verification failed")
        return None

    except jwt.PyJWTError as e:
        logging.exception(e)
        return None
