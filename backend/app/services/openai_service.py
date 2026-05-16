"""OpenAI-powered recommendation service."""

import json
import uuid
from typing import List, Optional

from openai import OpenAI
from sqlalchemy import select, desc, func

from app.core.config import settings
from app.core.database import get_session
from app.models.product import Product
from app.models.recommendation import Recommendation
from app.models.review import Review

client: OpenAI = None  # type: ignore


def init_openai() -> None:
    """Initialize the OpenAI client."""
    global client
    if settings.OPENAI_API_KEY:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)


async def get_similar_products(product_id: str, limit: int = 4) -> List[dict]:
    """Find products similar to the given product."""
    try:
        product_uuid = uuid.UUID(product_id)
    except ValueError:
        return []

    async with get_session() as session:
        result = await session.execute(select(Product).where(Product.id == product_uuid))
        product = result.scalar_one_or_none()
        if not product:
            return []

        # Simple category-based similarity as fallback or primary
        result = await session.execute(
            select(Product)
            .where(Product.category == product.category)
            .where(Product.id != product.id)
            .limit(limit)
        )
        similar = result.scalars().all()
        
        # In a real app with OpenAI, we might use embeddings or keywords here.
        # For now, let's keep it simple or implement the keyword search if needed.
        # Given the original code had OpenAI keyword search:
        if client:
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a shopping assistant."},
                        {"role": "user", "content": f"Given the product '{product.name}' with description '{product.description}', list 5 related search keywords as a JSON array of strings under the key 'keywords'."}
                    ],
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                if content:
                    keywords = json.loads(content).get("keywords", [])
                    if keywords:
                        # Full text search in PostgreSQL would be better, but for now ilike
                        filters = [Product.name.ilike(f"%{kw}%") for kw in keywords] 
                        filters.append(Product.description.ilike(f"%{kw}%") for kw in keywords)
                        # Re-execute with keywords if desired
                        pass
            except Exception:
                pass

        return [
            {
                "id": str(p.id),
                "name": p.name,
                "price": p.price,
                "category": p.category,
                "images": p.images or []
            } for p in similar
        ]


async def get_personalized_recommendations(user_id: Optional[str], limit: int = 8) -> List[dict]:
    """Provide personalized recommendations based on purchase history and behavior."""
    async with get_session() as session:
        # Guest users get top-rated products
        if not user_id:
            return await _get_top_rated_products(session, limit)
        
        user_uuid = uuid.UUID(user_id)
        
        # Get user's purchase history and preferences
        user_rec_result = await session.execute(
            select(Recommendation).where(Recommendation.user_id == user_uuid)
        )
        user_rec = user_rec_result.scalar_one_or_none()
        
        # Get user's reviews to understand preferences
        reviews_result = await session.execute(
            select(Review).where(Review.user_id == user_uuid)
        )
        user_reviews = reviews_result.scalars().all()
        
        if not user_rec or not user_rec.purchased_product_ids:
            return await _get_top_rated_products(session, limit)
        
        try:
            purchased_ids = user_rec.purchased_product_ids or []
            purchased_uuids = [uuid.UUID(pid) for pid in purchased_ids]
        except (TypeError, ValueError):
            purchased_uuids = []

        if not purchased_uuids:
            return await _get_top_rated_products(session, limit)
        
        # Enhanced recommendation algorithm
        recommendations = await _enhanced_recommendation_algorithm(
            session, user_uuid, purchased_uuids, user_reviews, limit
        )
        
        return recommendations


async def _get_top_rated_products(session, limit: int = 8) -> List[dict]:
    """Get top-rated products as fallback recommendations."""
    result = await session.execute(
        select(Product).order_by(desc(Product.average_rating)).limit(limit)
    )
    products = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "price": p.price,
            "category": p.category,
            "images": p.images or [],
            "average_rating": p.average_rating
        } for p in products
    ]


async def _enhanced_recommendation_algorithm(
    session, 
    user_id: uuid.UUID, 
    purchased_uuids: List[uuid.UUID], 
    user_reviews: List, 
    limit: int = 8
) -> List[dict]:
    """Enhanced recommendation algorithm using multiple factors."""
    
    # 1. Get categories of purchased products (weight: 40%)
    category_result = await session.execute(
        select(Product.category).where(Product.id.in_(purchased_uuids)).distinct()
    )
    purchased_categories = [row[0] for row in category_result.all()]
    
    # 2. Get highly rated products in purchased categories (excluding already purchased)
    category_recommendations = []
    if purchased_categories:
        category_result = await session.execute(
            select(Product)
            .where(Product.category.in_(purchased_categories))
            .where(Product.id.notin_(purchased_uuids))
            .order_by(desc(Product.average_rating))
            .limit(limit * 2)  # Get more to filter later
        )
        category_recommendations = category_result.scalars().all()
    
    # 3. Analyze user reviews to find preferred categories and price ranges
    preferred_categories = []
    preferred_price_range = (0, float('inf'))
    
    if user_reviews:
        # Find categories with highest average ratings from user
        category_ratings = {}
        for review in user_reviews:
            if review.product_id in purchased_uuids:
                product_result = await session.execute(
                    select(Product.category).where(Product.id == review.product_id)
                )
                category = product_result.scalar_one_or_none()
                if category:
                    if category not in category_ratings:
                        category_ratings[category] = []
                    category_ratings[category].append(review.rating)
        
        # Get top 2 categories by user rating
        if category_ratings:
            avg_ratings = [(cat, sum(ratings)/len(ratings)) for cat, ratings in category_ratings.items()]
            avg_ratings.sort(key=lambda x: x[1], reverse=True)
            preferred_categories = [cat for cat, rating in avg_ratings[:2]]
        
        # Find user's preferred price range based on purchased products
        price_result = await session.execute(
            select(Product.price).where(Product.id.in_(purchased_uuids))
        )
        purchased_prices = [row[0] for row in price_result.all()]
        if purchased_prices:
            avg_price = sum(purchased_prices) / len(purchased_prices)
            std_dev = (sum((p - avg_price) ** 2 for p in purchased_prices) / len(purchased_prices)) ** 0.5
            preferred_price_range = (max(0, avg_price - std_dev), avg_price + std_dev)
    
    # 4. Get trending products (recently popular) - weight: 20%
    trending_result = await session.execute(
        select(Product)
        .where(Product.id.notin_(purchased_uuids))
        .order_by(desc(Product.review_count), desc(Product.average_rating))
        .limit(limit)
    )
    trending_products = trending_result.scalars().all()
    
    # 5. Combine recommendations with scoring
    all_candidates = []
    
    # Add category-based recommendations
    for product in category_recommendations:
        score = 1.0  # Base score
        
        # Boost score if in preferred categories
        if product.category in preferred_categories:
            score += 0.5
        
        # Boost score if in preferred price range
        if preferred_price_range[0] <= product.price <= preferred_price_range[1]:
            score += 0.3
        
        # Boost score by rating
        score += product.average_rating * 0.2
        
        all_candidates.append((product, score))
    
    # Add trending products
    for product in trending_products:
        score = 0.8  # Slightly lower base score for trending
        
        # Boost if in preferred categories
        if product.category in preferred_categories:
            score += 0.4
        
        # Boost if in preferred price range
        if preferred_price_range[0] <= product.price <= preferred_price_range[1]:
            score += 0.2
        
        # Boost by popularity
        score += min(product.review_count / 10, 0.5)
        
        all_candidates.append((product, score))
    
    # 6. Remove duplicates and sort by score
    seen_ids = set()
    unique_candidates = []
    for product, score in sorted(all_candidates, key=lambda x: x[1], reverse=True):
        if product.id not in seen_ids:
            seen_ids.add(product.id)
            unique_candidates.append((product, score))
    
    # 7. Return top recommendations
    final_recommendations = unique_candidates[:limit]
    
    # 8. Use OpenAI for personalized recommendations if available
    if client and len(final_recommendations) > 0:
        try:
            # Get user's purchase history details
            purchased_products_result = await session.execute(
                select(Product).where(Product.id.in_(purchased_uuids))
            )
            purchased_products = purchased_products_result.scalars().all()
            
            # Create prompt for OpenAI
            purchase_history = ", ".join([p.name for p in purchased_products])
            candidate_products = ", ".join([p[0].name for p in final_recommendations])
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a personal shopping assistant that helps users discover products they'll love."},
                    {"role": "user", "content": f"A user has purchased these products: {purchase_history}. Based on their purchase history and preferences, which 3 of these candidate products would be the best recommendations: {candidate_products}? Respond with just the product names in order of preference, separated by commas."}
                ],
                max_tokens=100,
            )
            
            content = response.choices[0].message.content
            if content:
                # Try to reorder based on OpenAI recommendations
                recommended_names = [name.strip() for name in content.split(",")]
                name_to_product = {p[0].name: p for p in final_recommendations}
                
                # Reorder based on OpenAI suggestions
                reordered = []
                for name in recommended_names:
                    if name in name_to_product:
                        reordered.append(name_to_product[name])
                        del name_to_product[name]
                
                # Add remaining products
                for product_tuple in name_to_product.values():
                    reordered.append(product_tuple)
                
                final_recommendations = reordered[:limit]
        except Exception:
            pass  # Fallback to our algorithm if OpenAI fails
    
    return [
        {
            "id": str(p[0].id),
            "name": p[0].name,
            "price": p[0].price,
            "category": p[0].category,
            "images": p[0].images or [],
            "average_rating": p[0].average_rating,
            "recommendation_score": round(p[1], 2) if len(p) > 1 else None
        } for p in final_recommendations
    ]