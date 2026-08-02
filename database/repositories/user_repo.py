"""SQL repository for user operations"""

from database.models import User
from database.repositories.base_repo import BaseRepo


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