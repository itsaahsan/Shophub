"""Product review routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.schemas.review import ReviewCreate, ReviewResponse
from app.utils.helpers import serialize_docs, to_object_id, utc_now

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/{product_id}", response_model=list[ReviewResponse])
async def list_product_reviews(product_id: str):
    """List all reviews for a specific product."""
    db = get_db()
    cursor = db.reviews.find({"product_id": product_id}).sort("created_at", -1)
    reviews = await cursor.to_list(None)
    return serialize_docs(reviews)


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(body: ReviewCreate, user: dict = Depends(get_current_user)):
    """Post a review for a product (one per user)."""
    db = get_db()
    
    # Check if user already reviewed this product
    existing = await db.reviews.find_one({
        "product_id": body.product_id,
        "user_id": user["id"]
    })
    if existing:
        raise HTTPException(status_code=400, detail="Product already reviewed by this user")

    # Verify product exists
    product = await db.products.find_one({"_id": to_object_id(body.product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Save review
    review_doc = {
        "product_id": body.product_id,
        "user_id": user["id"],
        "user_name": user["name"],
        "rating": body.rating,
        "comment": body.comment,
        "created_at": utc_now(),
    }
    result = await db.reviews.insert_one(review_doc)
    review_doc["id"] = str(result.inserted_id)

    # Update product average rating and review count
    new_count = product.get("review_count", 0) + 1
    old_avg = product.get("average_rating", 0.0)
    new_avg = ((old_avg * (new_count - 1)) + body.rating) / new_count
    
    await db.products.update_one(
        {"_id": to_object_id(body.product_id)},
        {"$set": {"average_rating": new_avg, "review_count": new_count}}
    )

    return review_doc


@router.delete("/{review_id}")
async def delete_review(review_id: str, user: dict = Depends(get_current_user)):
    """Delete a review (own review or admin)."""
    db = get_db()
    review = await db.reviews.find_one({"_id": to_object_id(review_id)})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if review["user_id"] != user["id"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this review")

    await db.reviews.delete_one({"_id": to_object_id(review_id)})
    
    # Recalculate product rating (simplified: just decrement count, 
    # real production should re-average properly from all reviews)
    product = await db.products.find_one({"_id": to_object_id(review["product_id"])})
    if product and product.get("review_count", 0) > 0:
        new_count = product["review_count"] - 1
        if new_count == 0:
            new_avg = 0.0
        else:
            # This is an approximation. A full recalculation would be better.
            new_avg = ((product["average_rating"] * (new_count + 1)) - review["rating"]) / new_count
        
        await db.products.update_one(
            {"_id": to_object_id(review["product_id"])},
            {"$set": {"average_rating": new_avg, "review_count": new_count}}
        )

    return {"message": "Review deleted"}
