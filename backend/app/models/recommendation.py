from typing import List

from app.models.base import MongoBaseModel


class Recommendation(MongoBaseModel):
    """User recommendations based on purchase history."""

    user_id: str
    purchased_product_ids: List[str] = []
