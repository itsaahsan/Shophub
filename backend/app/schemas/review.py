"""Pydantic schemas for reviews and ratings."""

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    product_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=5, max_length=1000)


class ReviewResponse(BaseModel):
    id: str
    user_id: str
    user_name: str
    product_id: str
    rating: int
    comment: str
    created_at: str


class ReviewListResponse(BaseModel):
    reviews: list[ReviewResponse]
    average_rating: float
    total: int
