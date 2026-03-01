"""Pydantic schemas for orders."""

from pydantic import BaseModel, Field


class ShippingAddress(BaseModel):
    full_name: str = Field(..., min_length=2)
    address_line: str = Field(..., min_length=5)
    city: str
    state: str
    zip_code: str
    country: str = "US"


class CheckoutRequest(BaseModel):
    shipping_address: ShippingAddress


class OrderItemResponse(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int
    image: str | None = None


class OrderResponse(BaseModel):
    id: str
    user_id: str
    items: list[OrderItemResponse]
    total: float
    status: str  # pending, paid, shipped, delivered, cancelled
    shipping_address: dict
    stripe_session_id: str | None = None
    created_at: str


class OrderListResponse(BaseModel):
    orders: list[OrderResponse]
    total: int
