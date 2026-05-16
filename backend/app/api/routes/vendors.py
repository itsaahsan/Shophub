"""Vendor management routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc, func

from app.core.database import get_session
from app.core.redis import cache_delete_pattern, cache_get, cache_set
from app.middleware.auth import get_current_admin, get_current_user
from app.models.user import User, UserRole
from app.models.vendor import Vendor
from app.schemas.vendor import VendorCreate, VendorResponse, VendorListResponse, VendorUpdate

router = APIRouter(prefix="/vendors", tags=["vendors"])


@router.post("", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    body: VendorCreate, 
    current_user: dict = Depends(get_current_user)
):
    """Create a vendor profile for the current user."""
    user_uuid = uuid.UUID(current_user["id"])
    
    # Check if user already has a vendor profile
    async with get_session() as session:
        result = await session.execute(select(Vendor).where(Vendor.user_id == user_uuid))
        existing_vendor = result.scalar_one_or_none()
        
        if existing_vendor:
            raise HTTPException(
                status_code=400, 
                detail="User already has a vendor profile"
            )
        
        # Update user role to vendor
        user_result = await session.execute(select(User).where(User.id == user_uuid))
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.role = UserRole.VENDOR.value
        
        # Create vendor profile
        vendor = Vendor(
            user_id=user_uuid,
            **body.model_dump(),
        )
        
        session.add(vendor)
        await session.commit()
        await session.refresh(vendor)
    
    await cache_delete_pattern("vendors:*")
    return VendorResponse(
        id=str(vendor.id),
        user_id=str(vendor.user_id),
        shop_name=vendor.shop_name,
        description=vendor.description,
        logo=vendor.logo,
        banner=vendor.banner,
        is_verified=vendor.is_verified,
        rating=vendor.rating,
        review_count=vendor.review_count,
        created_at=vendor.created_at,
        updated_at=vendor.updated_at,
    )


@router.get("/me", response_model=VendorResponse)
async def get_my_vendor_profile(
    current_user: dict = Depends(get_current_user)
):
    """Get the current user's vendor profile."""
    user_uuid = uuid.UUID(current_user["id"])
    
    async with get_session() as session:
        result = await session.execute(select(Vendor).where(Vendor.user_id == user_uuid))
        vendor = result.scalar_one_or_none()
        
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor profile not found")
        
        return VendorResponse(
            id=str(vendor.id),
            user_id=str(vendor.user_id),
            shop_name=vendor.shop_name,
            description=vendor.description,
            logo=vendor.logo,
            banner=vendor.banner,
            is_verified=vendor.is_verified,
            rating=vendor.rating,
            review_count=vendor.review_count,
            created_at=vendor.created_at,
            updated_at=vendor.updated_at,
        )


@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(vendor_id: str):
    """Get a vendor by ID."""
    try:
        vendor_uuid = uuid.UUID(vendor_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    async with get_session() as session:
        result = await session.execute(select(Vendor).where(Vendor.user_id == vendor_uuid))
        vendor = result.scalar_one_or_none()
        
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")
        
        return VendorResponse(
            id=str(vendor.id),
            user_id=str(vendor.user_id),
            shop_name=vendor.shop_name,
            description=vendor.description,
            logo=vendor.logo,
            banner=vendor.banner,
            is_verified=vendor.is_verified,
            rating=vendor.rating,
            review_count=vendor.review_count,
            created_at=vendor.created_at,
            updated_at=vendor.updated_at,
        )


@router.get("", response_model=VendorListResponse)
async def list_vendors(
    page: int = Query(1, ge=1),
    per_page: int = Query(24, ge=1, le=100),
    search: str = Query(""),
    verified: bool = Query(None),
    sort: str = Query("newest", pattern="^(newest|rating|name)$"),
):
    """List all vendors with filtering and pagination."""
    cache_key = f"vendors:{page}:{per_page}:{search}:{verified}:{sort}"
    cached = await cache_get(cache_key)
    if cached:
        return cached
    
    async with get_session() as session:
        query = select(Vendor)
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.where(
                Vendor.shop_name.ilike(search_term)
            )
        
        if verified is not None:
            query = query.where(Vendor.is_verified == verified)
        
        # Sort
        sort_map = {
            "newest": desc(Vendor.created_at),
            "rating": desc(Vendor.rating),
            "name": asc(Vendor.shop_name),
        }
        query = query.order_by(sort_map.get(sort, desc(Vendor.created_at)))
        
        # Count and paginate
        count_result = await session.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0
        pages = max(1, (total + per_page - 1) // per_page)
        
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        result = await session.execute(query)
        vendors = result.scalars().all()
        
        response = VendorListResponse(
            vendors=[
                VendorResponse(
                    id=str(v.id),
                    user_id=str(v.user_id),
                    shop_name=v.shop_name,
                    description=v.description,
                    logo=v.logo,
                    banner=v.banner,
                    is_verified=v.is_verified,
                    rating=v.rating,
                    review_count=v.review_count,
                    created_at=v.created_at,
                    updated_at=v.updated_at,
                ) for v in vendors
            ],
            total=total,
            page=page,
            pages=pages,
        )
        
        result_dict = response.model_dump()
        await cache_set(cache_key, result_dict)
        return response


@router.put("/me", response_model=VendorResponse)
async def update_my_vendor_profile(
    body: VendorUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update the current user's vendor profile."""
    user_uuid = uuid.UUID(current_user["id"])
    
    async with get_session() as session:
        result = await session.execute(select(Vendor).where(Vendor.user_id == user_uuid))
        vendor = result.scalar_one_or_none()
        
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor profile not found")
        
        update_data = body.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(vendor, key, value)
        
        await session.commit()
        await session.refresh(vendor)
    
    await cache_delete_pattern("vendors:*")
    
    return VendorResponse(
        id=str(vendor.id),
        user_id=str(vendor.user_id),
        shop_name=vendor.shop_name,
        description=vendor.description,
        logo=vendor.logo,
        banner=vendor.banner,
        is_verified=vendor.is_verified,
        rating=vendor.rating,
        review_count=vendor.review_count,
        created_at=vendor.created_at,
        updated_at=vendor.updated_at,
    )


@router.put("/{vendor_id}/verify", response_model=VendorResponse)
async def verify_vendor(
    vendor_id: str,
    _: dict = Depends(get_current_admin)
):
    """Verify a vendor (admin only)."""
    try:
        vendor_uuid = uuid.UUID(vendor_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    async with get_session() as session:
        result = await session.execute(select(Vendor).where(Vendor.user_id == vendor_uuid))
        vendor = result.scalar_one_or_none()
        
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")
        
        vendor.is_verified = True
        await session.commit()
        await session.refresh(vendor)
    
    await cache_delete_pattern("vendors:*")
    
    return VendorResponse(
        id=str(vendor.id),
        user_id=str(vendor.user_id),
        shop_name=vendor.shop_name,
        description=vendor.description,
        logo=vendor.logo,
        banner=vendor.banner,
        is_verified=vendor.is_verified,
        rating=vendor.rating,
        review_count=vendor.review_count,
        created_at=vendor.created_at,
        updated_at=vendor.updated_at,
    )


@router.delete("/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vendor(
    vendor_id: str,
    _: dict = Depends(get_current_admin)
):
    """Delete a vendor (admin only)."""
    try:
        vendor_uuid = uuid.UUID(vendor_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    async with get_session() as session:
        result = await session.execute(select(Vendor).where(Vendor.user_id == vendor_uuid))
        vendor = result.scalar_one_or_none()
        
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")
        
        # Also update user role back to regular user
        user_result = await session.execute(select(User).where(User.id == vendor_uuid))
        user = user_result.scalar_one_or_none()
        
        if user:
            user.role = UserRole.USER.value
        
        await session.delete(vendor)
        await session.commit()
    
    await cache_delete_pattern("vendors:*")