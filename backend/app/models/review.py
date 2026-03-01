from pydantic import Field

from app.models.base import MongoBaseModel


class Review(MongoBaseModel):
    """Product review model for MongoDB."""

    product_id: str
    user_id: str
    user_name: str
    rating: int = Field(..., ge=1, le=5)
    comment: str
