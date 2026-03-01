"""Shopping cart routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.schemas.cart import CartResponse, CartUpdate
from app.utils.helpers import serialize_doc, to_object_id

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=CartResponse)
async def get_cart(user: dict = Depends(get_current_user)):
    """Retrieve the current user's shopping cart."""
    db = get_db()
    cart = await db.cart.find_one({"user_id": user["id"]})
    if not cart:
        # Return empty cart if not exists
        return CartResponse(user_id=user["id"], items=[])

    # Populating product details for each item
    items = []
    for item in cart.get("items", []):
        product = await db.products.find_one({"_id": to_object_id(item["product_id"])})
        if product:
            items.append({
                "product_id": item["product_id"],
                "quantity": item["quantity"],
                "name": product["name"],
                "price": product["price"],
                "image": product["images"][0] if product.get("images") else None,
                "stock": product.get("stock", 0)
            })

    return CartResponse(user_id=user["id"], items=items)


@router.post("/items")
async def add_to_cart(body: CartUpdate, user: dict = Depends(get_current_user)):
    """Add or update an item in the cart."""
    db = get_db()
    
    # Check if product exists and has stock
    product = await db.products.find_one({"_id": to_object_id(body.product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.get("stock", 0) < body.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    # Update or create cart
    # If item exists, update quantity, else add new item
    cart = await db.cart.find_one({"user_id": user["id"]})
    if not cart:
        await db.cart.insert_one({
            "user_id": user["id"],
            "items": [{"product_id": body.product_id, "quantity": body.quantity}]
        })
    else:
        # Check if item already in cart
        items = cart.get("items", [])
        found = False
        for item in items:
            if item["product_id"] == body.product_id:
                item["quantity"] = body.quantity
                found = True
                break
        
        if not found:
            items.append({"product_id": body.product_id, "quantity": body.quantity})
        
        await db.cart.update_one(
            {"user_id": user["id"]},
            {"$set": {"items": items}}
        )

    return {"message": "Cart updated"}


@router.delete("/items/{product_id}")
async def remove_from_cart(product_id: str, user: dict = Depends(get_current_user)):
    """Remove an item from the cart."""
    db = get_db()
    await db.cart.update_one(
        {"user_id": user["id"]},
        {"$pull": {"items": {"product_id": product_id}}}
    )
    return {"message": "Item removed from cart"}


@router.delete("")
async def clear_cart(user: dict = Depends(get_current_user)):
    """Clear all items from the cart."""
    db = get_db()
    await db.cart.update_one(
        {"user_id": user["id"]},
        {"$set": {"items": []}}
    )
    return {"message": "Cart cleared"}
