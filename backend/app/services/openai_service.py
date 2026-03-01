"""OpenAI-powered recommendation service."""

import json
from typing import List, Optional

from bson import ObjectId
from openai import OpenAI

from app.core.config import settings
from app.core.database import get_db
from app.utils.helpers import serialize_doc

client: OpenAI = None  # type: ignore


def init_openai() -> None:
    """Initialize the OpenAI client."""
    global client
    if settings.OPENAI_API_KEY:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)


async def get_similar_products(product: dict, limit: int = 4) -> List[dict]:
    """Find products similar to the given product using OpenAI and text matching."""
    db = get_db()
    # Get a proper ObjectId for exclusion
    product_oid = product.get("_id")
    if not product_oid:
        pid = product.get("id", "")
        product_oid = ObjectId(pid) if ObjectId.is_valid(pid) else None

    base_filter: dict = {"category": product["category"]}
    if product_oid:
        base_filter["_id"] = {"$ne": product_oid}

    if not client:
        cursor = db.products.find(base_filter).limit(limit)
        return [serialize_doc(d) for d in await cursor.to_list(limit)]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a shopping assistant."},
                {"role": "user", "content": f"Given the product '{product['name']}' with description '{product['description']}', list 5 related search keywords as a JSON array of strings."}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        if content:
            keywords = json.loads(content).get("keywords", [])
            if keywords:
                query = {**base_filter, "$text": {"$search": " ".join(keywords)}}
                cursor = db.products.find(query).limit(limit)
                results = [serialize_doc(d) for d in await cursor.to_list(limit)]
                if results:
                    return results
    except Exception:
        pass

    cursor = db.products.find(base_filter).limit(limit)
    return [serialize_doc(d) for d in await cursor.to_list(limit)]


async def get_personalized_recommendations(user_id: Optional[str], limit: int = 8) -> List[dict]:
    """Provide personalized recommendations based on purchase history."""
    db = get_db()

    # Guest users get top-rated products
    if not user_id:
        cursor = db.products.find().sort("average_rating", -1).limit(limit)
        return [serialize_doc(d) for d in await cursor.to_list(limit)]

    user_rec = await db.recommendations.find_one({"user_id": user_id})

    if not user_rec or not user_rec.get("purchased_product_ids"):
        cursor = db.products.find().sort("average_rating", -1).limit(limit)
        return [serialize_doc(d) for d in await cursor.to_list(limit)]

    purchased_ids = user_rec["purchased_product_ids"]
    # Convert string IDs to ObjectIds for MongoDB _id queries
    purchased_oids = [ObjectId(pid) for pid in purchased_ids if ObjectId.is_valid(pid)]

    cursor = db.products.find({"_id": {"$in": purchased_oids}})
    purchased_products = await cursor.to_list(len(purchased_oids))
    categories = list(set(p["category"] for p in purchased_products))

    cursor = db.products.find({
        "category": {"$in": categories},
        "_id": {"$nin": purchased_oids}
    }).sort("average_rating", -1).limit(limit)

    return [serialize_doc(d) for d in await cursor.to_list(limit)]
