from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class User:
    """Represents a row in the users table."""
    username: str
    email: str
    first_name: str
    last_name: str
    password_hash: str
    created_at: datetime | None = None
    id: int | None = None

    @classmethod
    def from_dict(cls, data: dict) -> User:
        return cls(
            id=data.get("id"),
            username=data["username"],
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            password_hash=data["password_hash"],
            created_at=data.get("created_at"),
        )

    def to_public_dict(self) -> dict:
        """Safe representation for API responses that never expose password_hash."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@dataclass
class Category:
    """Represents a row in the categories table."""
    name: str
    id: int | None = None

    @classmethod
    def from_dict(cls, data: dict) -> Category:
        return cls(
            id=data.get("id"),
            name=data["name"],
        )


@dataclass
class Expense:
    """Represents a row in the expenses table."""
    cost: Decimal
    description: str | None
    category_id: int
    user_id: int
    created_at: datetime | None = None
    id: int | None = None

    @classmethod
    def from_dict(cls, data: dict) -> Expense:
        return cls(
            id=data.get("id"),
            cost=Decimal(str(data["cost"])),
            description=data.get("description"),
            category_id=data["category_id"],
            user_id=data["user_id"],
            created_at=data.get("created_at"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "cost": str(self.cost),
            "description": self.description,
            "category_id": self.category_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }