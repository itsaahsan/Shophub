"""Admin-only dashboard routes for statistics and overview."""

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends

from app.core.database import get_db
from app.middleware.auth import get_current_admin
from app.utils.helpers import serialize_doc, serialize_docs

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
async def get_stats(_: dict = Depends(get_current_admin)):
    """Retrieve high-level dashboard statistics (Admin only)."""
    db = get_db()
    
    # 1. Total sales and total revenue
    cursor = db.orders.find({"status": "paid"})
    paid_orders = await cursor.to_list(None)
    
    total_revenue = sum(o.get("total", 0.0) for o in paid_orders)
    total_sales = len(paid_orders)
    
    # 2. Total users
    total_users = await db.users.count_documents({})
    
    # 3. Total products
    total_products = await db.products.count_documents({})
    
    # 4. Recent orders (last 5)
    cursor = db.orders.find().sort("created_at", -1).limit(5)
    recent_orders = [serialize_doc(o) for o in await cursor.to_list(5)]
    
    # 5. Revenue by day (last 30 days)
    daily_revenue: dict[str, float] = defaultdict(float)
    for o in paid_orders:
        order_date = o.get("created_at", "")[:10]
        if order_date:
            daily_revenue[order_date] += o.get("total", 0.0)

    revenue_chart = [
        {"date": date, "revenue": round(rev, 2)}
        for date, rev in sorted(daily_revenue.items())
    ]
    
    return {
        "total_revenue": total_revenue,
        "total_sales": total_sales,
        "total_users": total_users,
        "total_products": total_products,
        "recent_orders": recent_orders,
        "revenue_chart": revenue_chart,
    }


@router.get("/users")
async def list_users(_: dict = Depends(get_current_admin)):
    """List all registered users."""
    db = get_db()
    cursor = db.users.find().sort("created_at", -1)
    users = await cursor.to_list(None)
    return serialize_docs(users)


@router.get("/orders")
async def list_all_orders(_: dict = Depends(get_current_admin)):
    """List all orders in the system."""
    db = get_db()
    cursor = db.orders.find().sort("created_at", -1)
    orders = await cursor.to_list(None)
    return serialize_docs(orders)
