"""Admin-only dashboard routes for statistics and overview."""

import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, desc

from app.core.database import get_session
from app.middleware.auth import get_current_admin
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.user import User
from app.utils.helpers import serialize_doc, serialize_docs

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
async def get_stats(_: dict = Depends(get_current_admin)):
    """Retrieve high-level dashboard statistics (Admin only)."""
    async with get_session() as session:
        # 1. Total sales and total revenue
        result = await session.execute(
            select(Order).where(Order.status == OrderStatus.PAID.value)
        )
        paid_orders = result.scalars().all()
        
        total_revenue = sum(o.total for o in paid_orders)
        total_sales = len(paid_orders)
        
        # 2. Total users
        result = await session.execute(select(func.count(User.id)))
        total_users = result.scalar() or 0
        
        # 3. Total products
        result = await session.execute(select(func.count(Product.id)))
        total_products = result.scalar() or 0
        
        # 4. Recent orders (last 5)
        result = await session.execute(
            select(Order).order_by(desc(Order.created_at)).limit(5)
        )
        recent_orders = result.scalars().all()
        recent_orders_serialized = []
        for o in recent_orders:
            recent_orders_serialized.append({
                "id": str(o.id),
                "user_id": str(o.user_id),
                "total": o.total,
                "status": o.status,
                "created_at": o.created_at.isoformat()
            })
        
        # 5. Revenue by day (last 30 days)
        daily_revenue: dict[str, float] = defaultdict(float)
        for o in paid_orders:
            order_date = o.created_at.strftime("%Y-%m-%d")
            daily_revenue[order_date] += o.total

        revenue_chart = [
            {"date": date, "revenue": round(rev, 2)}
            for date, rev in sorted(daily_revenue.items())
        ]
        
        return {
            "total_revenue": total_revenue,
            "total_sales": total_sales,
            "total_users": total_users,
            "total_products": total_products,
            "recent_orders": recent_orders_serialized,
            "revenue_chart": revenue_chart,
        }


@router.get("/users")
async def list_users(_: dict = Depends(get_current_admin)):
    """List all registered users."""
    async with get_session() as session:
        result = await session.execute(select(User).order_by(desc(User.created_at)))
        users = result.scalars().all()
        return [
            {
                "id": str(u.id),
                "name": u.name,
                "email": u.email,
                "role": u.role,
                "avatar": u.avatar,
                "created_at": u.created_at.isoformat()
            } for u in users
        ]


@router.get("/orders")
async def list_all_orders(_: dict = Depends(get_current_admin)):
    """List all orders in the system."""
    async with get_session() as session:
        result = await session.execute(select(Order).order_by(desc(Order.created_at)))
        orders = result.scalars().all()
        return [
            {
                "id": str(o.id),
                "user_id": str(o.user_id),
                "total": o.total,
                "status": o.status,
                "created_at": o.created_at.isoformat()
            } for o in orders
        ]
