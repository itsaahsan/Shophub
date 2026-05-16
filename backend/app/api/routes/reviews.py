"""Product review routes."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.middleware.auth import get_current_user
from app.models.review import Review
from app.models.product import Product
from app.schemas.review import ReviewCreate, ReviewResponse

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/{product_id}", response_model=list[ReviewResponse])
async def list_product_reviews(product_id: str):
    """List all reviews for a specific product."""
    try:
        product_uuid = uuid.UUID(product_id)
    except ValueError:
        return []
        
    async with get_session() as session:
        result = await session.execute(
            select(Review).where(Review.product_id == product_uuid).order_by(desc(Review.created_at))
        )
        reviews = result.scalars().all()
        return [
            ReviewResponse(
                id=str(r.id),
                product_id=str(r.product_id),
                user_id=str(r.user_id),
                user_name=r.user_name,
                rating=r.rating,
                comment=r.comment,
                created_at=r.created_at.isoformat()
            ) for r in reviews
        ]


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(body: ReviewCreate, user: dict = Depends(get_current_user)):
    """Post a review for a product (one per user)."""
    user_uuid = uuid.UUID(user["id"])
    product_uuid = uuid.UUID(body.product_id)
    
    async with get_session() as session:
        # Check if user already reviewed this product
        result = await session.execute(
            select(Review).where(Review.product_id == product_uuid).where(Review.user_id == user_uuid)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Product already reviewed by this user")

        # Verify product exists
        result = await session.execute(select(Product).where(Product.id == product_uuid))
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Save review
        review = Review(
            product_id=product_uuid,
            user_id=user_uuid,
            user_name=user["name"],
            rating=body.rating,
            comment=body.comment,
        )
        session.add(review)
        
        # Update product average rating and review count
        new_count = product.review_count + 1
        old_avg = product.average_rating
        new_avg = ((old_avg * (new_count - 1)) + body.rating) / new_count
        
        product.average_rating = new_avg
        product.review_count = new_count
        
        await session.commit()
        await session.refresh(review)

        return ReviewResponse(
            id=str(review.id),
            product_id=str(review.product_id),
            user_id=str(review.user_id),
            user_name=review.user_name,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at.isoformat()
        )


@router.delete("/{review_id}")
async def delete_review(review_id: str, user: dict = Depends(get_current_user)):
    """Delete a review (own review or admin)."""
    user_uuid = uuid.UUID(user["id"])
    try:
        review_uuid = uuid.UUID(review_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Review not found")
        
    async with get_session() as session:
        result = await session.execute(select(Review).where(Review.id == review_uuid))
        review = result.scalar_one_or_none()
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        if review.user_id != user_uuid and user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to delete this review")

        product_uuid = review.product_id
        rating = review.rating
        
        await session.delete(review)
        
        # Recalculate product rating
        result = await session.execute(select(Product).where(Product.id == product_uuid))
        product = result.scalar_one_or_none()
        if product and product.review_count > 0:
            new_count = product.review_count - 1
            if new_count == 0:
                new_avg = 0.0
            else:
                new_avg = ((product.average_rating * (new_count + 1)) - rating) / new_count
            
            product.average_rating = new_avg
            product.review_count = new_count
        
        await session.commit()

    return {"message": "Review deleted"}
