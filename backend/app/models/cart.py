from typing import List

from pydantic import Field

from app.models.base import MongoBaseModel


class CartItem(MongoBaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)


class Cart(MongoBaseModel):
    """Shopping cart model for MongoDB."""

    user_id: str
    items: List[CartItem] = []
