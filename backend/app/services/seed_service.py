"""One-time seeding of demo products with real image URLs."""

from app.core.database import get_db
from app.utils.helpers import utc_now


# Curated demo catalog with real product-style images (Unsplash/CDN).
# These are meant for local development/demo only.
SEED_PRODUCTS: list[dict] = [
    {
        "name": "Apple iPhone 15 Pro",
        "description": "Apple iPhone 15 Pro with A17 Pro chip, 6.1‑inch Super Retina XDR display, titanium design, and pro camera system.",
        "price": 999.0,
        "category": "Smartphones",
        "stock": 25,
        "images": [
            "https://images.unsplash.com/photo-1695048133142-4d4a980142d9?auto=format&fit=crop&w=900&q=80",
        ],
        "original_images": [
            "https://images.unsplash.com/photo-1695048133142-4d4a980142d9?auto=format&fit=crop&w=1600&q=80",
        ],
    },
    {
        "name": "MacBook Air 13\" M2",
        "description": "13‑inch MacBook Air with Apple M2 chip, 8‑core CPU, 8‑core GPU, 8GB unified memory, and 256GB SSD storage.",
        "price": 1199.0,
        "category": "Laptops",
        "stock": 15,
        "images": [
            "https://images.unsplash.com/photo-1517059224940-d4af9eec41e5?auto=format&fit=crop&w=900&q=80",
        ],
        "original_images": [
            "https://images.unsplash.com/photo-1517059224940-d4af9eec41e5?auto=format&fit=crop&w=1600&q=80",
        ],
    },
    {
        "name": "Sony WH-1000XM5 Wireless Headphones",
        "description": "Industry-leading noise canceling over-ear headphones with up to 30 hours of battery life and multi-device pairing.",
        "price": 399.0,
        "category": "Headphones",
        "stock": 40,
        "images": [
            "https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=900&q=80",
        ],
        "original_images": [
            "https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=1600&q=80",
        ],
    },
    {
        "name": "Apple Watch Series 9",
        "description": "Apple Watch Series 9 with always‑on Retina display, advanced health sensors, and all‑day battery life.",
        "price": 399.0,
        "category": "Wearables",
        "stock": 30,
        "images": [
            "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80",
        ],
        "original_images": [
            "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1600&q=80",
        ],
    },
    {
        "name": "Nintendo Switch OLED",
        "description": "Nintendo Switch with vibrant 7‑inch OLED screen, enhanced audio, and 64GB internal storage for portable and docked gaming.",
        "price": 349.0,
        "category": "Gaming",
        "stock": 20,
        "images": [
            "https://images.unsplash.com/photo-1580537659466-5c8da948ad18?auto=format&fit=crop&w=900&q=80",
        ],
        "original_images": [
            "https://images.unsplash.com/photo-1580537659466-5c8da948ad18?auto=format&fit=crop&w=1600&q=80",
        ],
    },
    {
        "name": "Samsung 49\" Odyssey G9 QLED Monitor",
        "description": "49‑inch curved QLED gaming monitor with 240Hz refresh rate, 1ms response time, and Dual QHD resolution.",
        "price": 1499.0,
        "category": "Monitors",
        "stock": 10,
        "images": [
            "https://images.unsplash.com/photo-1587202372775-98973d4a2c95?auto=format&fit=crop&w=900&q=80",
        ],
        "original_images": [
            "https://images.unsplash.com/photo-1587202372775-98973d4a2c95?auto=format&fit=crop&w=1600&q=80",
        ],
    },
    {
        "name": "Logitech MX Master 3S Mouse",
        "description": "Advanced wireless mouse with MagSpeed electromagnetic scrolling, ergonomic design, and multi-device connectivity.",
        "price": 129.0,
        "category": "Accessories",
        "stock": 60,
        "images": [
            "https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?auto=format&fit=crop&w=900&q=80",
        ],
        "original_images": [
            "https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?auto=format&fit=crop&w=1600&q=80",
        ],
    },
    {
        "name": "Apple iPad Air (M2)",
        "description": "10.9‑inch iPad Air with M2 chip, Liquid Retina display, Apple Pencil support, and all‑day battery life.",
        "price": 599.0,
        "category": "Tablets",
        "stock": 25,
        "images": [
            "https://images.unsplash.com/photo-1545239351-1141bd82e8a6?auto=format&fit=crop&w=900&q=80",
        ],
        "original_images": [
            "https://images.unsplash.com/photo-1545239351-1141bd82e8a6?auto=format&fit=crop&w=1600&q=80",
        ],
    },
    {
        "name": "Amazon Kindle Paperwhite",
        "description": "Waterproof 6.8‑inch e‑reader with adjustable warm light, high‑resolution display, and weeks‑long battery life.",
        "price": 149.0,
        "category": "E‑readers",
        "stock": 35,
        "images": [
            "https://images.unsplash.com/photo-1513475382585-d06e58bcb0ea?auto=format&fit=crop&w=900&q=80",
        ],
        "original_images": [
            "https://images.unsplash.com/photo-1513475382585-d06e58bcb0ea?auto=format&fit=crop&w=1600&q=80",
        ],
    },
    {
        "name": "Razer Huntsman Mini Keyboard",
        "description": "60% optical gaming keyboard with Razer Chroma RGB, doubleshot PBT keycaps, and detachable USB‑C cable.",
        "price": 129.0,
        "category": "Keyboards",
        "stock": 45,
        "images": [
            "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=900&q=80",
        ],
        "original_images": [
            "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1600&q=80",
        ],
    },
]


async def seed_products_if_empty() -> None:
    """Insert demo products if the catalog is empty."""
    db = get_db()
    count = await db.products.count_documents({})
    if count > 0:
        return

    now = utc_now()
    docs = []
    for product in SEED_PRODUCTS:
        doc = {
            **product,
            "average_rating": 0.0,
            "review_count": 0,
            "created_at": now,
        }
        docs.append(doc)

    await db.products.insert_many(docs)
    print(f"Seeded {len(docs)} demo products into the catalog.")

