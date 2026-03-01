"""Pydantic schemas for shopping cart."""

from pydantic import BaseModel, Field


class CartItemAdd(BaseModel):
    product_id: str
    quantity: int = Field(1, ge=1, le=99)


class CartUpdate(BaseModel):
    product_id: str
    quantity: int = Field(..., ge=1, le=99)


class CartItemResponse(BaseModel):
    product_id: str
    name: str
    price: float
    image: str | None = None
    quantity: int
    stock: int = 0


class CartResponse(BaseModel):
    user_id: str
    items: list[CartItemResponse]
