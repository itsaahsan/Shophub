"""Order and checkout routes with Stripe integration."""

import uuid
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_session
from app.middleware.auth import get_current_user
from app.models.cart import Cart
from app.models.order import Order, OrderItem, ShippingAddress, OrderStatus
from app.models.product import Product
from app.models.recommendation import Recommendation
from app.models.user import User
from app.schemas.order import (
    CheckoutRequest,
    OrderListResponse,
    OrderResponse,
)
from app.services.email_service import send_order_confirmation

router = APIRouter(prefix="/orders", tags=["orders"])

stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/checkout", response_model=dict)
async def create_checkout_session(
    body: CheckoutRequest, user: dict = Depends(get_current_user)
):
    """Create a Stripe Checkout Session for the current user's cart."""
    user_uuid = uuid.UUID(user["id"])
    async with get_session() as session:
        # Fetch cart
        result = await session.execute(
            select(Cart).where(Cart.user_id == user_uuid).options(selectinload(Cart.items))
        )
        cart = result.scalar_one_or_none()
        if not cart or not cart.items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        line_items = []
        order_items_data = []
        total = 0.0

        for item in cart.items:
            product_result = await session.execute(select(Product).where(Product.id == item.product_id))
            product = product_result.scalar_one_or_none()
            if not product:
                continue
            
            images = product.images or []

            # Calculate price in cents for Stripe
            line_items.append({
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": product.name,
                        "images": [images[0]] if images else [],
                    },
                    "unit_amount": int(product.price * 100),
                },
                "quantity": item.quantity,
            })
            
            order_items_data.append({
                "product_id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": item.quantity,
                "image": images[0] if images else None,
            })
            total += product.price * item.quantity

        if not line_items:
            raise HTTPException(status_code=400, detail="No valid items in cart")

        # Create session
        try:
            stripe_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=f"{settings.FRONTEND_URL}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/cart",
                customer_email=user["email"],
                metadata={
                    "user_id": user["id"],
                },
            )
            
            # Create shipping address
            shipping_addr = ShippingAddress(
                full_name=body.shipping_address.full_name,
                address_line=body.shipping_address.address_line,
                city=body.shipping_address.city,
                state=body.shipping_address.state,
                zip_code=body.shipping_address.zip_code,
                country=body.shipping_address.country,
            )
            session.add(shipping_addr)
            await session.flush()

            # Create pending order in DB
            order = Order(
                user_id=user_uuid,
                total=total,
                status=OrderStatus.PENDING.value,
                shipping_address_id=shipping_addr.id,
                stripe_session_id=stripe_session.id,
            )
            session.add(order)
            await session.flush()

            for item_data in order_items_data:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item_data["product_id"],
                    name=item_data["name"],
                    price=item_data["price"],
                    quantity=item_data["quantity"],
                    image=item_data["image"],
                )
                session.add(order_item)
            
            await session.commit()
            
            return {"id": stripe_session.id, "url": stripe_session.url}
        except Exception as e:
            await session.rollback()
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
        stripe_session = event["data"]["object"]
        session_id = stripe_session["id"]
        
        async with get_session() as session:
            # Find order by session ID and update to paid
            result = await session.execute(
                select(Order).where(Order.stripe_session_id == session_id).options(selectinload(Order.items))
            )
            order = result.scalar_one_or_none()
            
            if order:
                order.status = OrderStatus.PAID.value
                
                # Update stock for each product
                for item in order.items:
                    product_result = await session.execute(select(Product).where(Product.id == item.product_id))
                    product = product_result.scalar_one_or_none()
                    if product:
                        product.stock -= item.quantity
                
                # Clear user cart
                cart_result = await session.execute(
                    select(Cart).where(Cart.user_id == order.user_id).options(selectinload(Cart.items))
                )
                cart = cart_result.scalar_one_or_none()
                if cart:
                    for cart_item in cart.items:
                        await session.delete(cart_item)
                
                # Update recommendations history
                rec_result = await session.execute(
                    select(Recommendation).where(Recommendation.user_id == order.user_id)
                )
                rec = rec_result.scalar_one_or_none()
                new_product_ids = [str(i.product_id) for i in order.items]
                
                if not rec:
                    rec = Recommendation(
                        user_id=order.user_id,
                        purchased_product_ids=new_product_ids
                    )
                    session.add(rec)
                else:
                    existing_ids = rec.purchased_product_ids or []
                    updated_ids = list(set(existing_ids) | set(new_product_ids))
                    rec.purchased_product_ids = updated_ids
                
                await session.commit()
                
                # Send confirmation email
                user_result = await session.execute(select(User).where(User.id == order.user_id))
                user = user_result.scalar_one_or_none()
                if user:
                    # Map order to dict for email service
                    order_dict = {
                        "id": str(order.id),
                        "total": order.total,
                        "status": order.status,
                        "created_at": order.created_at.isoformat(),
                        "items": [
                            {
                                "name": i.name,
                                "price": i.price,
                                "quantity": i.quantity,
                                "image": i.image
                            } for i in order.items
                        ]
                    }
                    send_order_confirmation(user.email, order_dict)

    return {"status": "success"}


@router.get("", response_model=OrderListResponse)
async def list_user_orders(user: dict = Depends(get_current_user)):
    """List orders for the current user."""
    user_uuid = uuid.UUID(user["id"])
    async with get_session() as session:
        result = await session.execute(
            select(Order)
            .where(Order.user_id == user_uuid)
            .options(selectinload(Order.items), selectinload(Order.shipping_address))
            .order_by(desc(Order.created_at))
        )
        orders = result.scalars().all()
        
        order_responses = []
        for o in orders:
            order_responses.append({
                "id": str(o.id),
                "user_id": str(o.user_id),
                "total": o.total,
                "status": o.status,
                "created_at": o.created_at.isoformat(),
                "shipping_address": {
                    "full_name": o.shipping_address.full_name,
                    "address_line": o.shipping_address.address_line,
                    "city": o.shipping_address.city,
                    "state": o.shipping_address.state,
                    "zip_code": o.shipping_address.zip_code,
                    "country": o.shipping_address.country,
                },
                "items": [
                    {
                        "product_id": str(i.product_id),
                        "name": i.name,
                        "price": i.price,
                        "quantity": i.quantity,
                        "image": i.image
                    } for i in o.items
                ]
            })
    
    return OrderListResponse(
        orders=order_responses,
        total=len(order_responses)
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, user: dict = Depends(get_current_user)):
    """Get a single order by ID."""
    user_uuid = uuid.UUID(user["id"])
    try:
        order_uuid = uuid.UUID(order_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Order not found")
        
    async with get_session() as session:
        result = await session.execute(
            select(Order)
            .where(Order.id == order_uuid)
            .where(Order.user_id == user_uuid)
            .options(selectinload(Order.items), selectinload(Order.shipping_address))
        )
        o = result.scalar_one_or_none()
        if not o:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return {
            "id": str(o.id),
            "user_id": str(o.user_id),
            "total": o.total,
            "status": o.status,
            "created_at": o.created_at.isoformat(),
            "shipping_address": {
                "full_name": o.shipping_address.full_name,
                "address_line": o.shipping_address.address_line,
                "city": o.shipping_address.city,
                "state": o.shipping_address.state,
                "zip_code": o.shipping_address.zip_code,
                "country": o.shipping_address.country,
            },
            "items": [
                {
                    "product_id": str(i.product_id),
                    "name": i.name,
                    "price": i.price,
                    "quantity": i.quantity,
                    "image": i.image
                } for i in o.items
            ]
        }


@router.post("/{order_id}/cancel")
async def cancel_order(order_id: str, user: dict = Depends(get_current_user)):
    """Cancel an order (only if pending)."""
    user_uuid = uuid.UUID(user["id"])
    try:
        order_uuid = uuid.UUID(order_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Order not found")
        
    async with get_session() as session:
        result = await session.execute(
            select(Order)
            .where(Order.id == order_uuid)
            .where(Order.user_id == user_uuid)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order.status != OrderStatus.PENDING.value:
            raise HTTPException(status_code=400, detail=f"Cannot cancel order with status '{order.status}'")
        
        order.status = OrderStatus.CANCELLED.value
        await session.commit()
        
    return {"message": "Order cancelled"}
