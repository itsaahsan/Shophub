"""Shopping cart routes."""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.middleware.auth import get_current_user
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.schemas.cart import CartResponse, CartUpdate

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=CartResponse)
async def get_cart(user: dict = Depends(get_current_user)):
    """Retrieve the current user's shopping cart."""
    user_uuid = uuid.UUID(user["id"])
    async with get_session() as session:
        result = await session.execute(
            select(Cart)
            .where(Cart.user_id == user_uuid)
            .options(selectinload(Cart.items))
        )
        cart = result.scalar_one_or_none()
        
        if not cart:
            return CartResponse(user_id=user["id"], items=[])

        # Fetch product details for all items
        item_responses = []
        for item in cart.items:
            product_result = await session.execute(select(Product).where(Product.id == item.product_id))
            product = product_result.scalar_one_or_none()
            if product:
                images = product.images or []
                item_responses.append({
                    "product_id": str(item.product_id),
                    "quantity": item.quantity,
                    "name": product.name,
                    "price": product.price,
                    "image": images[0] if images else None,
                    "stock": product.stock
                })

        return CartResponse(user_id=user["id"], items=item_responses)


@router.post("/items")
async def add_to_cart(body: CartUpdate, user: dict = Depends(get_current_user)):
    """Add or update an item in the cart."""
    user_uuid = uuid.UUID(user["id"])
    try:
        product_uuid = uuid.UUID(body.product_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Product not found")
    
    async with get_session() as session:
        # Check if product exists and has stock
        result = await session.execute(select(Product).where(Product.id == product_uuid))
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        if product.stock < body.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")

        # Get or create cart
        result = await session.execute(select(Cart).where(Cart.user_id == user_uuid).options(selectinload(Cart.items)))
        cart = result.scalar_one_or_none()
        
        if not cart:
            cart = Cart(user_id=user_uuid)
            session.add(cart)
            await session.flush() # Get cart ID
            
        # Check if item already in cart
        item = next((i for i in cart.items if i.product_id == product_uuid), None)
        if item:
            item.quantity = body.quantity
        else:
            item = CartItem(cart_id=cart.id, product_id=product_uuid, quantity=body.quantity)
            session.add(item)
        
        await session.commit()

    return {"message": "Cart updated"}


@router.delete("/items/{product_id}")
async def remove_from_cart(product_id: str, user: dict = Depends(get_current_user)):
    """Remove an item from the cart."""
    user_uuid = uuid.UUID(user["id"])
    try:
        product_uuid = uuid.UUID(product_id)
    except ValueError:
        return {"message": "Item removed from cart"}
    
    async with get_session() as session:
        result = await session.execute(
            select(Cart).where(Cart.user_id == user_uuid).options(selectinload(Cart.items))
        )
        cart = result.scalar_one_or_none()
        if cart:
            item = next((i for i in cart.items if i.product_id == product_uuid), None)
            if item:
                await session.delete(item)
                await session.commit()
                
    return {"message": "Item removed from cart"}


@router.delete("")
async def clear_cart(user: dict = Depends(get_current_user)):
    """Clear all items from the cart."""
    user_uuid = uuid.UUID(user["id"])
    
    async with get_session() as session:
        result = await session.execute(
            select(Cart).where(Cart.user_id == user_uuid).options(selectinload(Cart.items))
        )
        cart = result.scalar_one_or_none()
        if cart:
            for item in cart.items:
                await session.delete(item)
            await session.commit()
            
    return {"message": "Cart cleared"}
