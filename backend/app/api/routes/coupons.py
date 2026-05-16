"""Coupon routes for applying and managing promo codes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.coupon import Coupon
from app.models.user import User
from app.api.routes.auth import get_current_user

router = APIRouter(prefix="/coupons", tags=["coupons"])


@router.post("/apply")
async def apply_coupon(
    code: str,
    cart_total: float,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Apply a coupon code to the current cart total."""
    result = await session.execute(select(Coupon).where(Coupon.code == code))
    coupon = result.scalar_one_or_none()

    if not coupon or not coupon.active:
        raise HTTPException(status_code=404, detail="Invalid or inactive coupon")

    if coupon.expires_at and coupon.expires_at < __import__("datetime").datetime.now(__import__("datetime").timezone.utc):
        raise HTTPException(status_code=400, detail="Coupon expired")

    if coupon.uses >= coupon.max_uses:
        raise HTTPException(status_code=400, detail="Coupon usage limit reached")

    if cart_total < (coupon.min_purchase or 0):
        raise HTTPException(status_code=400, detail="Minimum purchase not met")

    if coupon.discount_type == "percentage":
        discount = cart_total * (coupon.discount_value / 100)
    else:
        discount = min(coupon.discount_value, cart_total)

    return {
        "discount": round(discount, 2),
        "new_total": round(cart_total - discount, 2),
        "coupon_code": code,
    }
