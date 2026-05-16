"""AI Assistant routes for natural language product discovery."""

import json
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, or_

from app.core.database import get_session
from app.middleware.auth import get_optional_user
from app.models.product import Product
from app.services.openai_service import client

router = APIRouter(prefix="/ai", tags=["ai"])


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []


class ChatResponse(BaseModel):
    reply: str
    products: List[dict] = []


@router.post("/chat", response_model=ChatResponse)
async def ai_chat(
    body: ChatRequest,
    user: dict | None = Depends(get_optional_user)
):
    """Chat with the AI Shopping Assistant to find products."""
    if not client:
        raise HTTPException(status_code=503, detail="AI Service currently unavailable")

    try:
        # 1. Use OpenAI to extract intent and search keywords
        intent_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful shopping assistant for Shophub. Extract 2-3 search keywords from the user message to find products. Respond in JSON format: {\"keywords\": [\"kw1\", \"kw2\"], \"search_required\": true/false}"},
                {"role": "user", "content": body.message}
            ],
            response_format={"type": "json_object"}
        )
        
        intent_data = json.loads(intent_response.choices[0].message.content or "{}")
        keywords = intent_data.get("keywords", [])
        
        found_products = []
        if keywords:
            async with get_session() as session:
                # Search products by keywords (simple ilike for now)
                filters = []
                for kw in keywords:
                    filters.append(Product.name.ilike(f"%{kw}%"))
                    filters.append(Product.description.ilike(f"%{kw}%"))
                    filters.append(Product.category.ilike(f"%{kw}%"))
                
                result = await session.execute(
                    select(Product).where(or_(*filters)).limit(4)
                )
                products_models = result.scalars().all()
                found_products = [
                    {
                        "id": str(p.id),
                        "name": p.name,
                        "price": p.price,
                        "category": p.category,
                        "images": p.images or [],
                        "average_rating": p.average_rating
                    } for p in products_models
                ]

        # 2. Formulate the final response
        products_context = ""
        if found_products:
            products_context = "I found these products for you: " + ", ".join([p["name"] for p in found_products])
        else:
            products_context = "I couldn't find any specific products matching that exactly, but I can help you search for something else!"

        final_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a friendly and helpful shopping assistant for Shophub. Use the provided context to answer the user's message warmly and concisely."},
                {"role": "system", "content": f"Context: {products_context}"},
                {"role": "user", "content": body.message}
            ],
            max_tokens=200
        )
        
        reply = final_response.choices[0].message.content or "How can I help you today?"
        
        return ChatResponse(reply=reply, products=found_products)

    except Exception as e:
        print(f"AI Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process AI request")
