"""Authentication routes: signup, login, logout, refresh, Google OAuth."""

import uuid
from fastapi import APIRouter, HTTPException, Response, status, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.middleware.auth import get_current_user
from app.models.user import User, UserRole
from app.schemas.user import (
    GoogleLoginRequest,
    UserLogin,
    UserResponse,
    UserSignup,
    UserUpdate,
)
from app.utils.helpers import utc_now

router = APIRouter(prefix="/auth", tags=["auth"])

# Cookie settings
COOKIE_KWARGS = {
    "httponly": True,
    "secure": False,  # Set to True in production with HTTPS
    "samesite": "lax",  # More permissive for development
    "path": "/",
}


def _set_tokens(response: Response, user_id: str) -> None:
    """Set access and refresh token cookies on the response."""
    response.set_cookie(
        "access_token",
        create_access_token(user_id),
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **COOKIE_KWARGS,
    )
    response.set_cookie(
        "refresh_token",
        create_refresh_token(user_id),
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        **COOKIE_KWARGS,
    )


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSignup, response: Response):
    """Register a new user account."""
    try:
        async with get_session() as session:
            # Check if email exists
            result = await session.execute(select(User).where(User.email == body.email))
            if result.scalar_one_or_none():
                raise HTTPException(status_code=409, detail="Email already registered")

            user = User(
                name=body.name,
                email=body.email,
                password=hash_password(body.password),
                role=UserRole.USER.value,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

            user_id = str(user.id)
            _set_tokens(response, user_id)

            return UserResponse(id=user_id, name=user.name, email=user.email)

    except HTTPException:
        raise
    except ValueError as e:
        # Handle bcrypt/passlib password length errors gracefully
        msg = str(e)
        if "password cannot be longer than 72 bytes" in msg:
            raise HTTPException(
                status_code=400,
                detail="Password is too long. Please use 72 characters or fewer.",
            )
        raise HTTPException(status_code=500, detail=f"Signup failed: {msg}")
    except Exception as e:
        print(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")


@router.post("/login", response_model=UserResponse)
async def login(body: UserLogin, response: Response):
    """Authenticate with email and password."""
    async with get_session() as session:
        result = await session.execute(select(User).where(User.email == body.email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(body.password, user.password or ""):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_id = str(user.id)
        _set_tokens(response, user_id)

        return UserResponse(
            id=user_id, 
            name=user.name, 
            email=user.email, 
            role=user.role,
            avatar=user.avatar,
        )


@router.post("/logout")
async def logout(response: Response):
    """Clear authentication cookies."""
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"message": "Logged out"}


@router.post("/refresh")
async def refresh_token(request: Request, response: Response):
    """Issue a new access token using the refresh token."""
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")

    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    _set_tokens(response, payload["sub"])
    return {"message": "Token refreshed"}


@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    """Return the current authenticated user."""
    return UserResponse(
        id=user["id"], name=user["name"], email=user["email"],
        role=user.get("role", "user"), avatar=user.get("avatar"),
    )


@router.put("/me", response_model=UserResponse)
async def update_me(body: UserUpdate, user: dict = Depends(get_current_user)):
    """Update the current user's profile."""
    async with get_session() as session:
        user_uuid = uuid.UUID(user["id"])
        result = await session.execute(select(User).where(User.id == user_uuid))
        db_user = result.scalar_one_or_none()

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        if body.name:
            db_user.name = body.name

        await session.commit()
        await session.refresh(db_user)

        return UserResponse(
            id=str(db_user.id), 
            name=db_user.name, 
            email=db_user.email,
            role=db_user.role, 
            avatar=db_user.avatar,
        )


@router.post("/google", response_model=UserResponse)
async def google_login(body: GoogleLoginRequest, response: Response):
    """Authenticate or register via Google OAuth ID token."""
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests

    try:
        idinfo = id_token.verify_oauth2_token(
            body.credential,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    email = idinfo["email"]
    async with get_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            # Auto-register
            user = User(
                name=idinfo.get("name", email.split("@")[0]),
                email=email,
                password=None,  # No password for OAuth users
                role=UserRole.USER.value,
                avatar=idinfo.get("picture"),
                google_id=idinfo["sub"],
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

        user_id = str(user.id)
        _set_tokens(response, user_id)

        return UserResponse(
            id=user_id, 
            name=user.name, 
            email=user.email,
            role=user.role, 
            avatar=user.avatar,
        )