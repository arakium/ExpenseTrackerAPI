from pydantic import ValidationError as PydanticValidationError

class AppError(Exception):
    status_code = 400  # Default fallback

    def __init__(self, errors: dict | str):
        self.errors = errors
        super().__init__(errors)


class ValidationError(AppError):
    status_code = 400


class AuthenticationError(AppError):
    status_code = 401

class AuthorizationError(AppError):
    status_code = 403

class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409

def format_pydantic_errors(e: PydanticValidationError) -> dict:
    """Turns Pydantic errors into a clean {field: message} dictionary."""
    return {str(err["loc"][0]): err["msg"] for err in e.errors()}