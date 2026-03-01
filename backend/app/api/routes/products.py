"""Product catalog routes with Redis caching."""

import math

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status

from app.core.database import get_db
from app.core.redis import cache_delete_pattern, cache_get, cache_set
from app.middleware.auth import get_current_admin
from app.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.services.cloudinary_service import upload_image
from app.services.openai_service import get_similar_products
from app.utils.helpers import serialize_doc, to_object_id, utc_now

router = APIRouter(prefix="/products", tags=["products"])

PER_PAGE = 12


def _product_response(doc: dict) -> ProductResponse:
    """Map a MongoDB product document to a response schema."""
    return ProductResponse(
        id=doc["id"],
        name=doc["name"],
        description=doc["description"],
        price=doc["price"],
        category=doc["category"],
        stock=doc.get("stock", 0),
        images=doc.get("images", []),
        original_images=doc.get("original_images", []),
        average_rating=doc.get("average_rating", 0),
        review_count=doc.get("review_count", 0),
        created_at=doc.get("created_at", ""),
    )

@router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    search: str = Query("", max_length=200),
    category: str = Query(""),
    min_price: float = Query(0, ge=0),
    max_price: float = Query(0, ge=0),
    sort: str = Query("newest", pattern="^(newest|price_asc|price_desc)$"),
):
    """List products with search, filter, sort, and pagination. Redis cached."""
    cache_key = f"products:{page}:{search}:{category}:{min_price}:{max_price}:{sort}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    db = get_db()
    query: dict = {}

    if search:
        query["$text"] = {"$search": search}
    if category:
        query["category"] = category
    if min_price or max_price:
        price_filter = {}
        if min_price:
            price_filter["$gte"] = min_price
        if max_price:
            price_filter["$lte"] = max_price
        query["price"] = price_filter

    sort_map = {
        "newest": [("created_at", -1)],
        "price_asc": [("price", 1)],
        "price_desc": [("price", -1)],
    }

    total = await db.products.count_documents(query)
    pages = math.ceil(total / PER_PAGE) or 1
    skip = (page - 1) * PER_PAGE

    cursor = db.products.find(query).sort(sort_map[sort]).skip(skip).limit(PER_PAGE)
    docs = [serialize_doc(d) for d in await cursor.to_list(PER_PAGE)]

    result = ProductListResponse(
        products=[_product_response(d) for d in docs],
        total=total,
        page=page,
        pages=pages,
    ).model_dump()

    await cache_set(cache_key, result)
    return result


@router.get("/categories", response_model=list[str])
async def list_categories():
    """Return all distinct product categories."""
    cached = await cache_get("product_categories")
    if cached:
        return cached

    db = get_db()
    categories = await db.products.distinct("category")
    await cache_set("product_categories", categories, ttl=600)
    return categories


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    """Get a single product by ID."""
    cached = await cache_get(f"product:{product_id}")
    if cached:
        return cached

    db = get_db()
    doc = await db.products.find_one({"_id": to_object_id(product_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")

    result = _product_response(serialize_doc(doc)).model_dump()
    await cache_set(f"product:{product_id}", result)
    return result


@router.get("/{product_id}/similar")
async def similar_products(product_id: str):
    """Get AI-powered similar product recommendations."""
    db = get_db()
    product = await db.products.find_one({"_id": to_object_id(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    similar = await get_similar_products(product)
    return [_product_response(p).model_dump() for p in similar]


# --- Admin routes ---

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(body: ProductCreate, _: dict = Depends(get_current_admin)):
    """Create a new product (admin only)."""
    db = get_db()
    doc = {**body.model_dump(), "average_rating": 0, "review_count": 0, "created_at": utc_now()}
    result = await db.products.insert_one(doc)
    doc["id"] = str(result.inserted_id)

    await cache_delete_pattern("products:*")
    await cache_delete_pattern("product_categories")
    return _product_response(doc)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, body: ProductUpdate, _: dict = Depends(get_current_admin)):
    """Update a product (admin only)."""
    db = get_db()
    update_data = {k: v for k, v in body.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await db.products.find_one_and_update(
        {"_id": to_object_id(product_id)},
        {"$set": update_data},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")

    await cache_delete_pattern("products:*")
    await cache_delete_pattern(f"product:{product_id}")
    await cache_delete_pattern("product_categories")
    return _product_response(serialize_doc(result))


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str, _: dict = Depends(get_current_admin)):
    """Delete a product (admin only)."""
    db = get_db()
    result = await db.products.delete_one({"_id": to_object_id(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

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




