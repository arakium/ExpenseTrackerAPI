from datetime import datetime, timedelta, timezone
from typing import Any
import os

import jwt
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(raise_error_if_not_found=True))

SECRET_KEY = os.getenv("SECRET_JWT")


def encode_jwt(user_id: int) -> str:
    now = datetime.now(timezone.utc)

    return jwt.encode(
        payload={
            "sub": user_id,
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(weeks=4),
        },
        key=SECRET_KEY,
        algorithm="HS256",
    )


def decode_jwt(token: str) -> dict[str, Any]:
    return jwt.decode(
        jwt=token,
        key=SECRET_KEY,
        algorithms=["HS256"],
    )