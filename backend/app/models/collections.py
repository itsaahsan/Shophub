"""
MongoDB Collection Schemas (documentation reference).

These are the document structures stored in each collection.
Motor doesn't use ORM models — this file documents the expected shapes.

Collections:
-----------

users:
    _id: ObjectId
    name: str
    email: str (unique index)
    password: str (bcrypt hash, empty for OAuth users)
    role: "user" | "admin"
    avatar: str | null
    google_id: str | null
    created_at: str (ISO datetime)

products:
    _id: ObjectId
    name: str (text index)
    description: str (text index)
    price: float
    category: str (index)
    stock: int
    images: list[str]  (Cloudinary URLs)
    average_rating: float
    review_count: int
    created_at: str (ISO datetime)

orders:
    _id: ObjectId
    user_id: str (index)
    items: list[{product_id, name, price, quantity, image}]
    total: float
    status: "pending" | "paid" | "shipped" | "delivered" | "cancelled"
    shipping_address: {full_name, address_line, city, state, zip_code, country}
    stripe_session_id: str | null
    created_at: str (ISO datetime)

cart:
    _id: ObjectId
    user_id: str (unique index)
    items: list[{product_id, quantity}]

wishlist:
    _id: ObjectId
    user_id: str (unique index)
    items: list[{product_id, added_at}]

reviews:
    _id: ObjectId
    product_id: str (compound index with user_id, unique)
    user_id: str
    user_name: str
    rating: int (1-5)
    comment: str
    created_at: str (ISO datetime)

recommendations:
    _id: ObjectId
    user_id: str (index)
    purchased_product_ids: list[str]
"""
