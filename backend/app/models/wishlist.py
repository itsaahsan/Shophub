from datetime import datetime, timezone
from typing import List

from pydantic import Field

from app.models.base import MongoBaseModel


class WishlistItem(MongoBaseModel):
    product_id: str
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Wishlist(MongoBaseModel):
    """Wishlist model for MongoDB."""

    user_id: str
    items: List[WishlistItem] = []
