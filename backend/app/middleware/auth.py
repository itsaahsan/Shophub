"""JWT authentication middleware and dependency injectors."""

from fastapi import Depends, HTTPException, Request, status

from app.core.database import get_db
from app.core.security import decode_token
from bson import ObjectId


async def get_current_user(request: Request) -> dict:
    """Extract and validate JWT from httpOnly cookie. Returns the user document."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    user["id"] = str(user.pop("_id"))
    return user


async def get_current_admin(user: dict = Depends(get_current_user)) -> dict:
    """Ensure the current user has admin role."""
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


async def get_optional_user(request: Request) -> dict | None:
    """Return the current user if authenticated, else None. No error raised."""
    try:
        return await get_current_user(request)
    except HTTPException:
        return None
