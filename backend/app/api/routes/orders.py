"""Order and checkout routes with Stripe integration."""

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.core.config import settings
from app.core.database import get_db
from app.middleware.auth import get_current_user, get_optional_user
from app.schemas.order import (
    CheckoutRequest,
    OrderListResponse,
    OrderResponse,
)
from app.services.email_service import send_order_confirmation
from app.utils.helpers import serialize_doc, serialize_docs, to_object_id, utc_now

router = APIRouter(prefix="/orders", tags=["orders"])

stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/checkout", response_model=dict)
async def create_checkout_session(
    body: CheckoutRequest, user: dict = Depends(get_current_user)
):
    """Create a Stripe Checkout Session for the current user's cart."""
    db = get_db()
    cart = await db.cart.find_one({"user_id": user["id"]})
    if not cart or not cart.get("items"):
        raise HTTPException(status_code=400, detail="Cart is empty")

    line_items = []
    order_items = []
    total = 0.0

    for item in cart["items"]:
        product = await db.products.find_one({"_id": to_object_id(item["product_id"])})
        if not product:
            continue
        
        # Calculate price in cents for Stripe
        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": product["name"],
                    "images": [product["images"][0]] if product.get("images") else [],
                },
                "unit_amount": int(product["price"] * 100),
            },
            "quantity": item["quantity"],
        })
        
        order_items.append({
            "product_id": str(product["_id"]),
            "name": product["name"],
            "price": product["price"],
            "quantity": item["quantity"],
            "image": product["images"][0] if product.get("images") else None,
        })
        total += product["price"] * item["quantity"]

    if not line_items:
        raise HTTPException(status_code=400, detail="No valid items in cart")

    # Create session
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=f"{settings.FRONTEND_URL}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/cart",
            customer_email=user["email"],
            metadata={
                "user_id": user["id"],
                # We store a summary or we'll rely on the webhook to create the order
                # Actually, it's better to create a 'pending' order now
            },
        )
        
        # Create pending order in DB
        order_doc = {
            "user_id": user["id"],
            "items": order_items,
            "total": total,
            "status": "pending",
            "shipping_address": body.shipping_address.model_dump(),
            "stripe_session_id": session.id,
            "created_at": utc_now(),
        }
        await db.orders.insert_one(order_doc)
        
        return {"id": session.id, "url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Webhook to handle Stripe payment success/failure."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return Response(status_code=400)
    except stripe.SignatureVerificationError:
        return Response(status_code=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session["id"]
        
        db = get_db()
        # Find order by session ID and update to paid
        order = await db.orders.find_one_and_update(
            {"stripe_session_id": session_id},
            {"$set": {"status": "paid"}},
            return_document=True
        )
        
        if order:
            # Update stock for each product
            for item in order["items"]:
                await db.products.update_one(
                    {"_id": to_object_id(item["product_id"])},
                    {"$inc": {"stock": -item["quantity"]}}
                )
            
            # Clear user cart
            await db.cart.update_one(
                {"user_id": order["user_id"]},
                {"$set": {"items": []}}
            )
            
            # Update recommendations history
            await db.recommendations.update_one(
                {"user_id": order["user_id"]},
                {"$addToSet": {"purchased_product_ids": {"$each": [i["product_id"] for i in order["items"]]}}},
                upsert=True
            )
            
            # Send confirmation email
            user = await db.users.find_one({"_id": to_object_id(order["user_id"])})
            if user:
                send_order_confirmation(user["email"], serialize_doc(order))

    return {"status": "success"}


@router.get("", response_model=OrderListResponse)
async def list_user_orders(user: dict = Depends(get_current_user)):
    """List orders for the current user."""
    db = get_db()
    cursor = db.orders.find({"user_id": user["id"]}).sort("created_at", -1)
    orders = await cursor.to_list(None)
    
    return OrderListResponse(
        orders=[serialize_doc(o) for o in orders],
        total=len(orders)
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, user: dict = Depends(get_current_user)):
    """Get a single order by ID."""
    db = get_db()
    order = await db.orders.find_one({
        "_id": to_object_id(order_id),
        "user_id": user["id"]
    })
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return serialize_doc(order)


@router.post("/{order_id}/cancel")
async def cancel_order(order_id: str, user: dict = Depends(get_current_user)):
    """Cancel an order (only if pending)."""
    db = get_db()
    order = await db.orders.find_one({
        "_id": to_object_id(order_id),
        "user_id": user["id"]
    })
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"Cannot cancel order with status '{order['status']}'")
    
    await db.orders.update_one(
        {"_id": to_object_id(order_id)},
        {"$set": {"status": "cancelled"}}
    )
    return {"message": "Order cancelled"}
