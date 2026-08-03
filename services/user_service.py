from pydantic import ValidationError

from database.models import User
from database.repositories.user_repo import UserRepo
from utils import password
from utils.validators import ValidateSignupRequest


def signup(repo: UserRepo, username: str, email: str, firstname: str, lastname: str, plain_password: str) -> User:
    try:
        ValidateSignupRequest(
            username=username,
            email=email,
            first_name=firstname,
            last_name=lastname,
            password=plain_password
        )
    except ValidationError as e:
        field_errors = {err["loc"][0]: err["msg"] for err in e.errors()}
        raise ValueError(field_errors)
    hashed = password.generate_hash(plain_password.strip())
    new_user = User(
        id=None,
        username=username.strip(),
        email=email.strip(),
        first_name=firstname.strip(),
        last_name=lastname.strip(),
        password_hash=hashed,
        created_at=None
    )
    return repo.create_user(new_user)