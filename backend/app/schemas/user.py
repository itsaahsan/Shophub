"""Pydantic schemas for user-related request/response validation."""

from pydantic import BaseModel, EmailStr, Field


class UserSignup(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    # bcrypt hashes only the first 72 bytes of the password, so we cap
    # the accepted password length to avoid surprising truncation.
    password: str = Field(..., min_length=6, max_length=72)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class GoogleLoginRequest(BaseModel):
    credential: str  # Google ID token


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str = "user"
    avatar: str | None = None


class TokenRefreshResponse(BaseModel):
    message: str = "Token refreshed"


class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
