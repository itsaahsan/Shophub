"""Subscription schemas for API requests/responses."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"


class SubscriptionPlanBase(BaseModel):
    """Base subscription plan schema."""
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    price: float = Field(..., gt=0)
    billing_cycle: str = Field(..., pattern="^(monthly|yearly)$")
    features: list[str] = []
    is_active: bool = True
    stripe_price_id: Optional[str] = Field(None, max_length=100)


class SubscriptionPlanCreate(SubscriptionPlanBase):
    """Schema for creating a subscription plan."""
    pass


class SubscriptionPlanUpdate(BaseModel):
    """Schema for updating subscription plan."""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    billing_cycle: Optional[str] = Field(None, pattern="^(monthly|yearly)$")
    features: Optional[list[str]] = None
    is_active: Optional[bool] = None
    stripe_price_id: Optional[str] = Field(None, max_length=100)


class SubscriptionPlanResponse(SubscriptionPlanBase):
    """Subscription plan response schema."""
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SubscriptionBase(BaseModel):
    """Base subscription schema."""
    plan_id: str
    status: SubscriptionStatus
    start_date: datetime
    end_date: Optional[datetime] = None
    stripe_subscription_id: Optional[str] = Field(None, max_length=100)
    stripe_customer_id: Optional[str] = Field(None, max_length=100)


class SubscriptionCreate(BaseModel):
    """Schema for creating a subscription."""
    plan_id: str = Field(..., description="ID of the subscription plan")


class SubscriptionResponse(SubscriptionBase):
    """Subscription response schema."""
    id: str
    user_id: str
    plan: SubscriptionPlanResponse
    
    class Config:
        from_attributes = True


class SubscriptionListResponse(BaseModel):
    """List of subscriptions response."""
    subscriptions: list[SubscriptionResponse]
    total: int
    page: int
    pages: int