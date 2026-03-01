from enum import Enum
from typing import Optional

from pydantic import EmailStr, Field

from app.models.base import MongoBaseModel


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(MongoBaseModel):
    """User model for MongoDB."""

    name: str
    email: EmailStr
    password: Optional[str] = None  # Hashed password (optional for OAuth users)
    role: UserRole = UserRole.USER
    avatar: Optional[str] = None
    google_id: Optional[str] = None
    is_active: bool = True
