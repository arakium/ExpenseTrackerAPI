
from pydantic import BaseModel, EmailStr, Field, ValidationError, ConfigDict


class ValidateSignupRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_to_lower=True,
    )
    username: str = Field(
        min_length=1,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$"  # only letters, numbers, underscores
    )
    email: EmailStr
    first_name: str = Field(
        min_length=1,
        max_length=40,
        pattern=r"^[a-zA-Z\s]+$"  # only letters and spaces
    )
    last_name: str = Field(
        min_length=1,
        max_length=40,
        pattern=r"^[a-zA-Z\s]+$"
    )
    password: str = Field(min_length=8)


class ValidateLoginrequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_to_lower=True,
    )
    identifier: str = Field(min_length=1)
    password: str = Field(min_length=8)


