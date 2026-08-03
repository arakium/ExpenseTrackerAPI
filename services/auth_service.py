from typing import cast

import jwt
from jwt import ExpiredSignatureError
from pydantic import ValidationError
from database.repositories.user_repo import UserRepo
from utils import password
from utils.auth import encode_jwt, decode_jwt
from utils.validators import ValidateLoginRequest




def login(repo: UserRepo, identifier: str, plain_password: str) -> str:
    try:
        ValidateLoginRequest(
            identifier=identifier,
            password=plain_password,
        )
    except ValidationError as e:
        field_errors = {err["loc"][0]: err["msg"] for err in e.errors()}
        raise ValueError(field_errors)

    if "@" in identifier:
        user = repo.get_user_by_email(identifier)
    else:
        user = repo.get_user_by_username(identifier)

    if user is None:
        raise ValueError("Invalid credentials")

    if not password.check_hash(plain_password, user.password_hash):
        raise ValueError("Invalid credentials")

    return encode_jwt(cast(int, user.id))

def get_current_user_id(auth_header: str | None) -> int:
    if not auth_header or not auth_header.startswith("Bearer "):
        raise ValueError("Missing or invalid authorization token.")

    token = auth_header.removeprefix("Bearer ")

    try:
        payload = decode_jwt(token)
    except ExpiredSignatureError:
        raise ValueError("Expired token.")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token.")

    return payload['sub']