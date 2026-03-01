from enum import Enum
from typing import List, Optional

from pydantic import Field

from app.models.base import MongoBaseModel


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItem(MongoBaseModel):
    product_id: str
    name: str
    price: float
    quantity: int
    image: Optional[str] = None


class ShippingAddress(MongoBaseModel):
    full_name: str
    address_line: str
    city: str
    state: str
    zip_code: str
    country: str


class Order(MongoBaseModel):
    """Order model for MongoDB."""

    user_id: str
    items: List[OrderItem]
    total: float
    status: OrderStatus = OrderStatus.PENDING
    shipping_address: ShippingAddress
    stripe_session_id: Optional[str] = None
