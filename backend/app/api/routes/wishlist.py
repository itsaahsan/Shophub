"""Wishlist routes."""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.middleware.auth import get_current_user
from app.models.wishlist import Wishlist, WishlistItem
from app.models.product import Product
from app.schemas.wishlist import WishlistResponse, WishlistUpdate

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


@router.get("", response_model=WishlistResponse)
async def get_wishlist(user: dict = Depends(get_current_user)):
    """Retrieve the current user's wishlist."""
    user_uuid = uuid.UUID(user["id"])
    async with get_session() as session:
        result = await session.execute(
            select(Wishlist).where(Wishlist.user_id == user_uuid).options(selectinload(Wishlist.items))
        )
        wishlist = result.scalar_one_or_none()
        if not wishlist:
            return WishlistResponse(user_id=user["id"], items=[])

        items = []
        for item in wishlist.items:
            product_result = await session.execute(select(Product).where(Product.id == item.product_id))
            product = product_result.scalar_one_or_none()
            if product:
                images = product.images or []
                items.append({
                    "product_id": str(item.product_id),
                    "name": product.name,
                    "price": product.price,
                    "image": images[0] if images else None,
                    "added_at": item.added_at.isoformat()
                })

        return WishlistResponse(user_id=user["id"], items=items)


@router.post("/items")
async def add_to_wishlist(body: WishlistUpdate, user: dict = Depends(get_current_user)):
    """Add a product to the wishlist."""
    user_uuid = uuid.UUID(user["id"])
    try:
        product_uuid = uuid.UUID(body.product_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Product not found")
    
    async with get_session() as session:
        # Check if product exists
        result = await session.execute(select(Product).where(Product.id == product_uuid))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Product not found")

        # Get or create wishlist
        result = await session.execute(
            select(Wishlist).where(Wishlist.user_id == user_uuid).options(selectinload(Wishlist.items))
        )
        wishlist = result.scalar_one_or_none()
        if not wishlist:
            wishlist = Wishlist(user_id=user_uuid)
            session.add(wishlist)
            await session.flush()

        # Check if item already in wishlist
        item = next((i for i in wishlist.items if i.product_id == product_uuid), None)
        if not item:
            item = WishlistItem(wishlist_id=wishlist.id, product_id=product_uuid)
            session.add(item)
            await session.commit()
            
    return {"message": "Product added to wishlist"}


@router.delete("/items/{product_id}")
async def remove_from_wishlist(product_id: str, user: dict = Depends(get_current_user)):
    """Remove a product from the wishlist."""
    user_uuid = uuid.UUID(user["id"])
    try:
        product_uuid = uuid.UUID(product_id)
    except ValueError:
        return {"message": "Product removed from wishlist"}
    
    async with get_session() as session:
        result = await session.execute(
            select(Wishlist).where(Wishlist.user_id == user_uuid).options(selectinload(Wishlist.items))
        )
        wishlist = result.scalar_one_or_none()
        if wishlist:
            item = next((i for i in wishlist.items if i.product_id == product_uuid), None)
            if item:
                await session.delete(item)
                await session.commit()
                
    return {"message": "Product removed from wishlist"}
