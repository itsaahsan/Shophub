"""Personalized product recommendation routes."""

from fastapi import APIRouter, Depends

from app.middleware.auth import get_current_user, get_optional_user
from app.services.openai_service import get_personalized_recommendations
from app.utils.helpers import serialize_docs

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("")
async def list_recommendations(user: dict | None = Depends(get_optional_user)):
    """Get personalized product recommendations for the current user."""
    if not user:
        # Fallback for guest users (e.g. top rated)
        return await get_personalized_recommendations(None)
    
    recs = await get_personalized_recommendations(user["id"])
    return recs
