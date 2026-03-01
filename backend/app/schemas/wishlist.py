"""Pydantic schemas for wishlist."""

from pydantic import BaseModel


class WishlistUpdate(BaseModel):
    product_id: str


class WishlistItemResponse(BaseModel):
    product_id: str
    name: str
    price: float
    image: str | None = None
    added_at: str


class WishlistResponse(BaseModel):
    user_id: str
    items: list[WishlistItemResponse]
