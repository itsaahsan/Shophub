"""Product catalog routes with Redis caching."""

import math
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy import or_, and_, func, select, desc, asc
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.core.redis import cache_delete_pattern, cache_get, cache_set
from app.middleware.auth import get_current_admin, get_current_vendor
from app.models.product import Product
from app.models.vendor import Vendor
from app.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.services.cloudinary_service import upload_image

router = APIRouter(prefix="/products", tags=["products"])

DEFAULT_PER_PAGE = 24
MAX_PER_PAGE = 100


def _product_response(product: Product) -> ProductResponse:
    """Map a SQLAlchemy Product model to a response schema."""
    return ProductResponse(
        id=str(product.id),
        name=product.name,
        description=product.description,
        price=product.price,
        category=product.category,
        stock=product.stock,
        images=product.images or [],
        original_images=product.original_images or [],
        average_rating=product.average_rating,
        review_count=product.review_count,
        created_at=product.created_at.isoformat() if product.created_at else "",
        vendor_id=str(product.vendor_id) if product.vendor_id else None,
        vendor_name=product.vendor.shop_name if product.vendor else None,
    )


@router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(DEFAULT_PER_PAGE, ge=1, le=MAX_PER_PAGE),
    search: str = Query("", max_length=200),
    category: str = Query(""),
    min_price: float = Query(0, ge=0),
    max_price: float = Query(0, ge=0),
    sort: str = Query("newest", pattern="^(newest|price_asc|price_desc)$"),
    vendor_id: str = Query(""),
):
    """List products with search, filter, sort, and pagination. Redis cached."""
    cache_key = f"products:{page}:{per_page}:{search}:{category}:{min_price}:{max_price}:{sort}:{vendor_id}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    async with get_session() as session:
        query = select(Product).options(selectinload(Product.vendor))
        
        # Apply filters
        filters = []
        if search:
            search_term = f"%{search}%"
            filters.append(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.category.ilike(search_term),
                )
            )
        if category:
            filters.append(Product.category == category)
        if min_price > 0:
            filters.append(Product.price >= min_price)
        if max_price > 0:
            filters.append(Product.price <= max_price)
        if vendor_id:
            try:
                vendor_uuid = uuid.UUID(vendor_id)
                filters.append(Product.vendor_id == vendor_uuid)
            except ValueError:
                pass
        
        if filters:
            query = query.where(and_(*filters))
        
        # Sort
        sort_map = {
            "newest": desc(Product.created_at),
            "price_asc": asc(Product.price),
            "price_desc": desc(Product.price),
        }
        query = query.order_by(sort_map.get(sort, desc(Product.created_at)))
        
        # Count and paginate
        count_result = await session.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0
        pages = math.ceil(total / per_page) or 1
        
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        result = await session.execute(query)
        products = result.scalars().all()
        
        response = ProductListResponse(
            products=[_product_response(p) for p in products],
            total=total,
            page=page,
            pages=pages,
        )
        result_dict = response.model_dump()
        await cache_set(cache_key, result_dict)
        return response


@router.get("/categories", response_model=list[str])
async def list_categories():
    """Return all distinct product categories."""
    cached = await cache_get("product_categories")
    if cached:
        return cached

    async with get_session() as session:
        result = await session.execute(select(Product.category).distinct())
        categories = [row[0] for row in result.all() if row[0]]
        await cache_set("product_categories", categories, ttl=600)
        return categories


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    """Get a single product by ID."""
    cached = await cache_get(f"product:{product_id}")
    if cached:
        return cached

    try:
        product_uuid = uuid.UUID(product_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Product not found")
    
    async with get_session() as session:
        result = await session.execute(
            select(Product)
            .options(selectinload(Product.vendor))
            .where(Product.id == product_uuid)
        )
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        response = _product_response(product)
        result_dict = response.model_dump()
        await cache_set(f"product:{product_id}", result_dict)
        return response


@router.get("/{product_id}/similar")
async def similar_products(product_id: str):
    """Get AI-powered similar product recommendations."""
    try:
        product_uuid = uuid.UUID(product_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Product not found")
        
    async with get_session() as session:
        result = await session.execute(
            select(Product)
            .options(selectinload(Product.vendor))
            .where(Product.id == product_uuid)
        )
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get similar products by category
        result = await session.execute(
            select(Product)
            .options(selectinload(Product.vendor))
            .where(Product.category == product.category)
            .where(Product.id != product.id)
            .limit(4)
        )
        similar = result.scalars().all()
        return [_product_response(p).model_dump() for p in similar]


# --- Admin routes ---

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(body: ProductCreate, admin: dict = Depends(get_current_admin)):
    """Create a new product (admin only)."""
    async with get_session() as session:
        product_data = body.model_dump()
        vendor_id = None
        if product_data.get("vendor_id"):
            try:
                vendor_id = uuid.UUID(product_data["vendor_id"])
                # Verify vendor exists
                vendor_result = await session.execute(select(Vendor).where(Vendor.user_id == vendor_id))
                if not vendor_result.scalar_one_or_none():
                    vendor_id = None
            except ValueError:
                vendor_id = None
        
        product = Product(
            **product_data,
            average_rating=0,
            review_count=0,
            vendor_id=vendor_id,
        )
        session.add(product)
        await session.commit()
        await session.refresh(product)
    
    await cache_delete_pattern("products:*")
    await cache_delete_pattern("product_categories")
    return _product_response(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, body: ProductUpdate, _: dict = Depends(get_current_admin)):
    """Update a product (admin only)."""
    try:
        product_uuid = uuid.UUID(product_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Product not found")
        
    async with get_session() as session:
        result = await session.execute(select(Product).where(Product.id == product_uuid))
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        update_data = body.model_dump(exclude_unset=True)
        if "vendor_id" in update_data:
            try:
                vendor_id = uuid.UUID(update_data["vendor_id"])
                # Verify vendor exists
                vendor_result = await session.execute(select(Vendor).where(Vendor.user_id == vendor_id))
                if not vendor_result.scalar_one_or_none():
                    del update_data["vendor_id"]
                else:
                    update_data["vendor_id"] = vendor_id
            except ValueError:
                del update_data["vendor_id"]
        
        for key, value in update_data.items():
            setattr(product, key, value)
        
        await session.commit()
        await session.refresh(product)
    
    await cache_delete_pattern("products:*")
    await cache_delete_pattern(f"product:{product_id}")
    await cache_delete_pattern("product_categories")
    return _product_response(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str, _: dict = Depends(get_current_admin)):
    """Delete a product (admin only)."""
    try:
        product_uuid = uuid.UUID(product_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Product not found")
        
    async with get_session() as session:
        result = await session.execute(select(Product).where(Product.id == product_uuid))
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        await session.delete(product)
        await session.commit()
    
    await cache_delete_pattern("products:*")
    await cache_delete_pattern(f"product:{product_id}")
    await cache_delete_pattern("product_categories")


@router.post("/upload-image")
async def upload_product_image(
    file: UploadFile = File(...), _: dict = Depends(get_current_admin)
):
    """Upload a product image to Cloudinary (admin only)."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    url = await upload_image(file)
    return {"url": url}