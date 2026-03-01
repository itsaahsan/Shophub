"""Wishlist routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.schemas.wishlist import WishlistResponse, WishlistUpdate
from app.utils.helpers import serialize_doc, to_object_id, utc_now

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


@router.get("", response_model=WishlistResponse)
async def get_wishlist(user: dict = Depends(get_current_user)):
    """Retrieve the current user's wishlist."""
    db = get_db()
    wishlist = await db.wishlist.find_one({"user_id": user["id"]})
    if not wishlist:
        return WishlistResponse(user_id=user["id"], items=[])

    items = []
    for item in wishlist.get("items", []):
        product = await db.products.find_one({"_id": to_object_id(item["product_id"])})
        if product:
            items.append({
                "product_id": item["product_id"],
                "name": product["name"],
                "price": product["price"],
                "image": product["images"][0] if product.get("images") else None,
                "added_at": item.get("added_at", "")
            })

    return WishlistResponse(user_id=user["id"], items=items)


@router.post("/items")
async def add_to_wishlist(body: WishlistUpdate, user: dict = Depends(get_current_user)):
    """Add a product to the wishlist."""
    db = get_db()
    
    product = await db.products.find_one({"_id": to_object_id(body.product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.wishlist.update_one(
        {"user_id": user["id"]},
        {"$addToSet": {"items": {"product_id": body.product_id, "added_at": utc_now()}}},
        upsert=True
    )
    return {"message": "Product added to wishlist"}


@router.delete("/items/{product_id}")
async def remove_from_wishlist(product_id: str, user: dict = Depends(get_current_user)):
    """Remove a product from the wishlist."""
    db = get_db()
    await db.wishlist.update_one(
        {"user_id": user["id"]},
        {"$pull": {"items": {"product_id": product_id}}}
    )
    return {"message": "Product removed from wishlist"}
