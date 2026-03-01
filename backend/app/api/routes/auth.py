"""Authentication routes: signup, login, logout, refresh, Google OAuth."""

from fastapi import APIRouter, HTTPException, Response, status

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.middleware.auth import get_current_user
from app.schemas.user import (
    GoogleLoginRequest,
    UserLogin,
    UserResponse,
    UserSignup,
    UserUpdate,
)
from app.utils.helpers import utc_now, to_object_id
from fastapi import Depends, Request

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
        db = get_db()

        if await db.users.find_one({"email": body.email}):
            raise HTTPException(status_code=409, detail="Email already registered")

        user_doc = {
            "name": body.name,
            "email": body.email,
            "password": hash_password(body.password),
            "role": "user",
            "avatar": None,
            "created_at": utc_now(),
        }
        result = await db.users.insert_one(user_doc)
        user_id = str(result.inserted_id)

        _set_tokens(response, user_id)

        return UserResponse(id=user_id, name=body.name, email=body.email)
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
    db = get_db()
    user = await db.users.find_one({"email": body.email})

    if not user or not verify_password(body.password, user.get("password", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id = str(user["_id"])
    _set_tokens(response, user_id)

    return UserResponse(
        id=user_id, name=user["name"], email=user["email"], role=user.get("role", "user"),
        avatar=user.get("avatar"),
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
    db = get_db()
    update_data = {}
    if body.name:
        update_data["name"] = body.name
    
    if update_data:
        await db.users.update_one(
            {"_id": to_object_id(user["id"])},
            {"$set": update_data},
        )

    # Fetch updated user
    updated_user = await db.users.find_one({"_id": to_object_id(user["id"])})
    return UserResponse(
        id=str(updated_user["_id"]), 
        name=updated_user["name"], 
        email=updated_user["email"],
        role=updated_user.get("role", "user"), 
        avatar=updated_user.get("avatar"),
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
    db = get_db()
    user = await db.users.find_one({"email": email})

    if not user:
        # Auto-register
        user_doc = {
            "name": idinfo.get("name", email.split("@")[0]),
            "email": email,
            "password": "",  # No password for OAuth users
            "role": "user",
            "avatar": idinfo.get("picture"),
            "google_id": idinfo["sub"],
            "created_at": utc_now(),
        }
        result = await db.users.insert_one(user_doc)
        user_id = str(result.inserted_id)
        user = {**user_doc, "id": user_id}
    else:
        user_id = str(user["_id"])
        user["id"] = user_id

    _set_tokens(response, user_id)

    return UserResponse(
        id=user["id"], name=user["name"], email=user["email"],
        role=user.get("role", "user"), avatar=user.get("avatar"),
    )