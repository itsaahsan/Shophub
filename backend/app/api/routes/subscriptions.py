"""Subscription management routes with Stripe integration."""

import uuid
from datetime import datetime, timedelta
from typing import Optional

import stripe
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import select, desc, func, and_, or_
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_session
from app.core.redis import cache_delete_pattern, cache_get, cache_set
from app.middleware.auth import get_current_admin, get_current_user
from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionListResponse,
    SubscriptionPlanCreate,
    SubscriptionPlanResponse,
    SubscriptionPlanUpdate,
    SubscriptionResponse,
)

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post(
    "/plans", 
    response_model=SubscriptionPlanResponse, 
    status_code=status.HTTP_201_CREATED
)
async def create_subscription_plan(
    body: SubscriptionPlanCreate,
    _: dict = Depends(get_current_admin)
):
    """Create a new subscription plan (admin only)."""
    async with get_session() as session:
        # Create Stripe product and price
        try:
            stripe_product = stripe.Product.create(
                name=body.name,
                description=body.description,
            )
            
            stripe_price = stripe.Price.create(
                product=stripe_product.id,
                unit_amount=int(body.price * 100),  # Convert to cents
                currency="usd",
                recurring={"interval": body.billing_cycle},
            )
            
            body.stripe_price_id = stripe_price.id
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Stripe error: {str(e)}"
            )
        
        plan = SubscriptionPlan(**body.model_dump())
        session.add(plan)
        await session.commit()
        await session.refresh(plan)
    
    await cache_delete_pattern("subscription_plans:*")
    return SubscriptionPlanResponse(
        id=str(plan.id),
        **body.model_dump(),
        created_at=plan.created_at,
        updated_at=plan.updated_at,
    )


@router.get("/plans", response_model=list[SubscriptionPlanResponse])
async def list_subscription_plans():
    """List all available subscription plans."""
    cached = await cache_get("subscription_plans:all")
    if cached:
        return cached
    
    async with get_session() as session:
        result = await session.execute(
            select(SubscriptionPlan)
            .where(SubscriptionPlan.is_active == True)
            .order_by(desc(SubscriptionPlan.created_at))
        )
        plans = result.scalars().all()
        
        response = [
            SubscriptionPlanResponse(
                id=str(p.id),
                name=p.name,
                description=p.description,
                price=p.price,
                billing_cycle=p.billing_cycle,
                features=p.features or [],
                is_active=p.is_active,
                stripe_price_id=p.stripe_price_id,
                created_at=p.created_at,
                updated_at=p.updated_at,
            ) for p in plans
        ]
        
        await cache_set("subscription_plans:all", response)
        return response


@router.get("/plans/{plan_id}", response_model=SubscriptionPlanResponse)
async def get_subscription_plan(plan_id: str):
    """Get a subscription plan by ID."""
    try:
        plan_uuid = uuid.UUID(plan_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    async with get_session() as session:
        result = await session.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.id == plan_uuid)
        )
        plan = result.scalar_one_or_none()
        
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        return SubscriptionPlanResponse(
            id=str(plan.id),
            name=plan.name,
            description=plan.description,
            price=plan.price,
            billing_cycle=plan.billing_cycle,
            features=plan.features or [],
            is_active=plan.is_active,
            stripe_price_id=plan.stripe_price_id,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
        )


@router.put("/plans/{plan_id}", response_model=SubscriptionPlanResponse)
async def update_subscription_plan(
    plan_id: str,
    body: SubscriptionPlanUpdate,
    _: dict = Depends(get_current_admin)
):
    """Update a subscription plan (admin only)."""
    try:
        plan_uuid = uuid.UUID(plan_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    async with get_session() as session:
        result = await session.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.id == plan_uuid)
        )
        plan = result.scalar_one_or_none()
        
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        update_data = body.model_dump(exclude_unset=True)
        
        # Handle Stripe updates if price changes
        if "price" in update_data and plan.stripe_price_id:
            try:
                stripe.Price.modify(
                    plan.stripe_price_id,
                    active=update_data["price"] > 0,
                )
                # Create new price
                new_price = stripe.Price.create(
                    product=stripe.Price.retrieve(plan.stripe_price_id).product,
                    unit_amount=int(update_data["price"] * 100),
                    currency="usd",
                    recurring={"interval": plan.billing_cycle},
                )
                update_data["stripe_price_id"] = new_price.id
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Stripe error: {str(e)}"
                )
        
        for key, value in update_data.items():
            setattr(plan, key, value)
        
        await session.commit()
        await session.refresh(plan)
    
    await cache_delete_pattern("subscription_plans:*")
    
    return SubscriptionPlanResponse(
        id=str(plan.id),
        name=plan.name,
        description=plan.description,
        price=plan.price,
        billing_cycle=plan.billing_cycle,
        features=plan.features or [],
        is_active=plan.is_active,
        stripe_price_id=plan.stripe_price_id,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
    )


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription_plan(
    plan_id: str,
    _: dict = Depends(get_current_admin)
):
    """Delete a subscription plan (admin only)."""
    try:
        plan_uuid = uuid.UUID(plan_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    async with get_session() as session:
        result = await session.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.id == plan_uuid)
        )
        plan = result.scalar_one_or_none()
        
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        # Deactivate associated Stripe price if exists
        if plan.stripe_price_id:
            try:
                stripe.Price.modify(plan.stripe_price_id, active=False)
            except Exception:
                pass
        
        await session.delete(plan)
        await session.commit()
    
    await cache_delete_pattern("subscription_plans:*")


@router.post("/checkout", response_model=dict)
async def create_subscription_checkout(
    body: SubscriptionCreate,
    user: dict = Depends(get_current_user)
):
    """Create a Stripe Checkout Session for subscription."""
    user_uuid = uuid.UUID(user["id"])
    
    async with get_session() as session:
        # Get plan
        result = await session.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.id == uuid.UUID(body.plan_id))
        )
        plan = result.scalar_one_or_none()
        
        if not plan or not plan.is_active:
            raise HTTPException(status_code=404, detail="Plan not found or inactive")
        
        if not plan.stripe_price_id:
            raise HTTPException(status_code=400, detail="Plan not configured for payments")
        
        # Get or create Stripe customer
        user_result = await session.execute(select(User).where(User.id == user_uuid))
        db_user = user_result.scalar_one_or_none()
        
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        stripe_customer_id = db_user.stripe_customer_id
        
        if not stripe_customer_id:
            stripe_customer = stripe.Customer.create(
                email=user["email"],
                name=user["name"],
                metadata={"user_id": user["id"]}
            )
            stripe_customer_id = stripe_customer.id
            db_user.stripe_customer_id = stripe_customer_id
            await session.commit()
        
        # Create checkout session
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price": plan.stripe_price_id,
                    "quantity": 1,
                }],
                mode="subscription",
                success_url=f"{settings.FRONTEND_URL}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/subscription/plans",
                customer=stripe_customer_id,
                metadata={
                    "user_id": user["id"],
                    "plan_id": body.plan_id,
                },
            )
            
            return {
                "session_id": checkout_session.id,
                "url": checkout_session.url
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Stripe error: {str(e)}"
            )


@router.post("/webhook")
async def stripe_subscription_webhook(request: Request):
    """Webhook to handle Stripe subscription events."""
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
    
    async with get_session() as session:
        if event["type"] == "checkout.session.completed":
            stripe_session = event["data"]["object"]
            
            if stripe_session.get("metadata", {}).get("plan_id"):
                # This is a subscription checkout
                user_id = stripe_session["metadata"]["user_id"]
                plan_id = stripe_session["metadata"]["plan_id"]
                
                user_uuid = uuid.UUID(user_id)
                plan_uuid = uuid.UUID(plan_id)
                
                # Get subscription from Stripe
                subscription_id = stripe_session["subscription"]
                stripe_sub = stripe.Subscription.retrieve(subscription_id)
                
                # Create or update subscription in DB
                result = await session.execute(
                    select(Subscription).where(Subscription.user_id == user_uuid)
                )
                existing_sub = result.scalar_one_or_none()
                
                if existing_sub:
                    # Cancel existing subscription
                    existing_sub.status = SubscriptionStatus.CANCELLED.value
                
                # Create new subscription
                subscription = Subscription(
                    user_id=user_uuid,
                    plan_id=plan_uuid,
                    status=SubscriptionStatus.ACTIVE.value,
                    start_date=datetime.now(),
                    end_date=None,  # Will be set when cancelled
                    stripe_subscription_id=stripe_sub.id,
                    stripe_customer_id=stripe_session["customer"],
                )
                
                session.add(subscription)
                await session.commit()
        
        elif event["type"] == "customer.subscription.deleted":
            stripe_sub = event["data"]["object"]
            
            # Find and update subscription
            result = await session.execute(
                select(Subscription).where(
                    Subscription.stripe_subscription_id == stripe_sub.id
                )
            )
            subscription = result.scalar_one_or_none()
            
            if subscription:
                subscription.status = SubscriptionStatus.CANCELLED.value
                subscription.end_date = datetime.now()
                await session.commit()
        
        elif event["type"] == "customer.subscription.updated":
            stripe_sub = event["data"]["object"]
            
            # Update subscription status
            result = await session.execute(
                select(Subscription).where(
                    Subscription.stripe_subscription_id == stripe_sub.id
                )
            )
            subscription = result.scalar_one_or_none()
            
            if subscription:
                status_map = {
                    "active": SubscriptionStatus.ACTIVE,
                    "canceled": SubscriptionStatus.CANCELLED,
                    "past_due": SubscriptionStatus.PAST_DUE,
                    "unpaid": SubscriptionStatus.UNPAID,
                }
                
                stripe_status = stripe_sub["status"]
                if stripe_status in status_map:
                    subscription.status = status_map[stripe_status].value
                    await session.commit()
    
    return {"status": "success"}


@router.get("", response_model=SubscriptionListResponse)
async def list_user_subscriptions(
    user: dict = Depends(get_current_user)
):
    """List subscriptions for the current user."""
    user_uuid = uuid.UUID(user["id"])
    
    async with get_session() as session:
        result = await session.execute(
            select(Subscription)
            .where(Subscription.user_id == user_uuid)
            .options(selectinload(Subscription.plan))
            .order_by(desc(Subscription.created_at))
        )
        subscriptions = result.scalars().all()
        
        response = SubscriptionListResponse(
            subscriptions=[
                SubscriptionResponse(
                    id=str(s.id),
                    user_id=str(s.user_id),
                    plan_id=str(s.plan_id),
                    status=s.status,
                    start_date=s.start_date,
                    end_date=s.end_date,
                    stripe_subscription_id=s.stripe_subscription_id,
                    stripe_customer_id=s.stripe_customer_id,
                    plan=SubscriptionPlanResponse(
                        id=str(s.plan.id),
                        name=s.plan.name,
                        description=s.plan.description,
                        price=s.plan.price,
                        billing_cycle=s.plan.billing_cycle,
                        features=s.plan.features or [],
                        is_active=s.plan.is_active,
                        stripe_price_id=s.plan.stripe_price_id,
                        created_at=s.plan.created_at,
                        updated_at=s.plan.updated_at,
                    ),
                ) for s in subscriptions
            ],
            total=len(subscriptions),
            page=1,
            pages=1,
        )
        
        return response


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: str,
    user: dict = Depends(get_current_user)
):
    """Get a specific subscription."""
    user_uuid = uuid.UUID(user["id"])
    
    try:
        sub_uuid = uuid.UUID(subscription_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    async with get_session() as session:
        result = await session.execute(
            select(Subscription)
            .where(Subscription.id == sub_uuid)
            .where(Subscription.user_id == user_uuid)
            .options(selectinload(Subscription.plan))
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        return SubscriptionResponse(
            id=str(subscription.id),
            user_id=str(subscription.user_id),
            plan_id=str(subscription.plan_id),
            status=subscription.status,
            start_date=subscription.start_date,
            end_date=subscription.end_date,
            stripe_subscription_id=subscription.stripe_subscription_id,
            stripe_customer_id=subscription.stripe_customer_id,
            plan=SubscriptionPlanResponse(
                id=str(subscription.plan.id),
                name=subscription.plan.name,
                description=subscription.plan.description,
                price=subscription.plan.price,
                billing_cycle=subscription.plan.billing_cycle,
                features=subscription.plan.features or [],
                is_active=subscription.plan.is_active,
                stripe_price_id=subscription.plan.stripe_price_id,
                created_at=subscription.plan.created_at,
                updated_at=subscription.plan.updated_at,
            ),
        )


@router.post("/{subscription_id}/cancel")
async def cancel_subscription(
    subscription_id: str,
    user: dict = Depends(get_current_user)
):
    """Cancel a subscription."""
    user_uuid = uuid.UUID(user["id"])
    
    try:
        sub_uuid = uuid.UUID(subscription_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    async with get_session() as session:
        result = await session.execute(
            select(Subscription)
            .where(Subscription.id == sub_uuid)
            .where(Subscription.user_id == user_uuid)
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        if subscription.status != SubscriptionStatus.ACTIVE.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel subscription with status '{subscription.status}'"
            )
        
        # Cancel in Stripe if applicable
        if subscription.stripe_subscription_id:
            try:
                stripe.Subscription.delete(subscription.stripe_subscription_id)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Stripe error: {str(e)}"
                )
        
        subscription.status = SubscriptionStatus.CANCELLED.value
        subscription.end_date = datetime.now()
        await session.commit()
    
    return {"message": "Subscription cancelled successfully"}


@router.get("/admin", response_model=SubscriptionListResponse)
async def list_all_subscriptions(
    page: int = Query(1, ge=1),
    per_page: int = Query(24, ge=1, le=100),
    status: Optional[str] = Query(None),
    plan_id: Optional[str] = Query(None),
    _: dict = Depends(get_current_admin)
):
    """List all subscriptions (admin only)."""
    cache_key = f"admin_subscriptions:{page}:{per_page}:{status}:{plan_id}"
    cached = await cache_get(cache_key)
    if cached:
        return cached
    
    async with get_session() as session:
        query = select(Subscription).options(selectinload(Subscription.plan))
        
        # Apply filters
        if status:
            query = query.where(Subscription.status == status)
        
        if plan_id:
            try:
                plan_uuid = uuid.UUID(plan_id)
                query = query.where(Subscription.plan_id == plan_uuid)
            except ValueError:
                pass
        
        # Count and paginate
        count_result = await session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0
        pages = max(1, (total + per_page - 1) // per_page)
        
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page).order_by(desc(Subscription.created_at))
        
        result = await session.execute(query)
        subscriptions = result.scalars().all()
        
        response = SubscriptionListResponse(
            subscriptions=[
                SubscriptionResponse(
                    id=str(s.id),
                    user_id=str(s.user_id),
                    plan_id=str(s.plan_id),
                    status=s.status,
                    start_date=s.start_date,
                    end_date=s.end_date,
                    stripe_subscription_id=s.stripe_subscription_id,
                    stripe_customer_id=s.stripe_customer_id,
                    plan=SubscriptionPlanResponse(
                        id=str(s.plan.id),
                        name=s.plan.name,
                        description=s.plan.description,
                        price=s.plan.price,
                        billing_cycle=s.plan.billing_cycle,
                        features=s.plan.features or [],
                        is_active=s.plan.is_active,
                        stripe_price_id=s.plan.stripe_price_id,
                        created_at=s.plan.created_at,
                        updated_at=s.plan.updated_at,
                    ),
                ) for s in subscriptions
            ],
            total=total,
            page=page,
            pages=pages,
        )
        
        result_dict = response.model_dump()
        await cache_set(cache_key, result_dict)
        return response