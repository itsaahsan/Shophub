"""Pydantic schemas for product-related request/response validation."""

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=10, max_length=5000)
    price: float = Field(..., gt=0)
    category: str = Field(..., min_length=2, max_length=100)
    stock: int = Field(..., ge=0)
    images: list[str] = []  # Cloudinary URLs
    original_images: list[str] = []  # Original image URLs (non‑thumbnail)


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(None, gt=0)
    category: str | None = None
    stock: int | None = Field(None, ge=0)
    images: list[str] | None = None
    original_images: list[str] | None = None


class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    stock: int
    images: list[str] = []
    original_images: list[str] = []
    average_rating: float = 0.0
    review_count: int = 0
    created_at: str


class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    total: int
    page: int
    pages: int
