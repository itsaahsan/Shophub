"""Coupon model for promotions."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Numeric, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Coupon(BaseModel):
    """Coupon/promo code model."""

    __tablename__ = "coupons"

    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    discount_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'percentage' or 'fixed'
    discount_value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    min_purchase: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), default=0)
    max_uses: Mapped[int] = mapped_column(Integer, default=100)
    uses: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
