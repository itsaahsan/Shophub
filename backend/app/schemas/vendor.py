"""Vendor schemas for API requests/responses."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class VendorBase(BaseModel):
    """Base vendor schema."""
    shop_name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    logo: Optional[str] = Field(None, max_length=500)
    banner: Optional[str] = Field(None, max_length=500)


class VendorCreate(VendorBase):
    """Schema for creating a vendor profile."""
    pass


class VendorUpdate(BaseModel):
    """Schema for updating vendor information."""
    shop_name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    logo: Optional[str] = Field(None, max_length=500)
    banner: Optional[str] = Field(None, max_length=500)


class VendorResponse(VendorBase):
    """Vendor response schema."""
    id: str
    user_id: str
    is_verified: bool
    rating: float
    review_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class VendorListResponse(BaseModel):
    """List of vendors response."""
    vendors: list[VendorResponse]
    total: int
    page: int
    pages: int