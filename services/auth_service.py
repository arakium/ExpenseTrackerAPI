from typing import cast

import jwt
from jwt import ExpiredSignatureError
from pydantic import ValidationError as PydanticValidationError

from database.repositories.user_repo import UserRepo
from exceptions import ValidationError, format_pydantic_errors, AuthenticationError
from utils import password
from utils.auth import encode_jwt, decode_jwt
from utils.validators import ValidateLoginRequest


def login(repo: UserRepo, identifier: str, plain_password: str) -> str:
    try:
        ValidateLoginRequest(
            identifier=identifier,
            password=plain_password,
        )
    except PydanticValidationError as e:
        raise ValidationError(format_pydantic_errors(e))

    if "@" in identifier:
        user = repo.get_user_by_email(identifier)
    else:
        user = repo.get_user_by_username(identifier)

    if user is None:
        raise AuthenticationError("Invalid credentials")

    if not password.check_hash(plain_password, user.password_hash):
        raise AuthenticationError("Invalid credentials")

    return encode_jwt(cast(int, user.id))

def get_current_user_id(auth_header: str | None) -> int:
    if not auth_header or not auth_header.startswith("Bearer "):
        raise AuthenticationError("Missing or invalid authorization token.")

    token = auth_header.removeprefix("Bearer ")

    try:
        payload = decode_jwt(token)
    except ExpiredSignatureError:
        raise AuthenticationError("Expired token.")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token.")

    return int(payload['sub'])