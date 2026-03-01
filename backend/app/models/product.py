from typing import List, Optional

from pydantic import Field

from app.models.base import MongoBaseModel


class Product(MongoBaseModel):
    """Product model for MongoDB."""

    name: str
    description: str
    price: float = Field(..., gt=0)
    category: str
    stock: int = Field(..., ge=0)
    images: List[str] = []
    average_rating: float = 0.0
    review_count: int = 0
