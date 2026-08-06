"""SQL repository for user operations"""
import psycopg

from database.models import User
from database.repositories.base_repo import BaseRepo
from exceptions import ConflictError


class UserRepo(BaseRepo):

    def get_user_by_username(self, username: str) -> User | None:
        data = self._fetch_one("""
            SELECT * FROM users 
            WHERE username = %s
        """, (username,))

        if data:
            return User.from_dict(data)
        else:
            return None

    def get_user_by_email(self, email: str) -> User | None:
        data = self._fetch_one("""
            SELECT * FROM users 
            WHERE email = %s
        """, (email,))
        if data:
            return User.from_dict(data)
        else:
            return None

    def create_user(self, user: User) -> User:
        try:
            data = self._fetch_one(
                """
                INSERT INTO users(username, first_name, last_name, email, password_hash)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    user.username,
                    user.first_name,
                    user.last_name,
                    user.email,
                    user.password_hash,
                )
            )
        except psycopg.errors.UniqueViolation as e:
            constraint = e.diag.constraint_name
            if constraint == "users_username_key":
                raise ConflictError({"error": {"username": "Username already in use"}})
            elif constraint == "users_email_key":
                raise ConflictError({"error": {"email": "Email already in use"}})
            else:
                raise ConflictError({"error": "A uniqueness constraint was violated"})
        if data is None:
            raise RuntimeError("User creation failed — no row returned from database")
        return User.from_dict(data)

    def delete_user(self, user_id: int) -> None:
        self._execute("""
                    DELETE FROM users WHERE id = %s
                """, (user_id,))

    def update_user(self, user: User) -> None:
        self._execute(
            """
            UPDATE users
            SET username      = %s,
                first_name    = %s,
                last_name     = %s,
                email         = %s,
                password_hash = %s
            WHERE id = %s
            """,
            (
                user.username,
                user.first_name,
                user.last_name,
                user.email,
                user.password_hash,
                user.id,
            )
        )

if __name__ == "__main__":
    pass