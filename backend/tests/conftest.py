"""Shared test fixtures for pytest."""

import asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.database import get_db, connect_db, close_db
from app.core.redis import connect_redis, close_redis
from app.core.security import hash_password, create_access_token
from bson import ObjectId


@pytest.fixture(scope="session")
def event_loop():
    """Create and set an event loop for the test session.

    The original implementation created a new loop but never set it as the
    current loop for the running thread.  AsyncIO objects (e.g., Motor's
    ``AsyncIOMotorClient``) bind to the loop retrieved via ``asyncio.get_event_loop``.
    When the test client (httpx) operates on a different loop, futures become
    attached to the wrong loop, resulting in ``RuntimeError: Future attached to a
    different loop`` errors.  By explicitly calling ``asyncio.set_event_loop`` we
    ensure all async components share the same loop throughout the test session.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_db():
    """Connect to test database once per session."""
    await connect_db()
    await connect_redis()
    yield
    await close_redis()
    await close_db()


@pytest.fixture
async def client(setup_db):
    """Async HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user(setup_db):
    """Create a test user and return user dict with auth cookie value."""
    db = get_db()
    user_doc = {
        "name": "Test User",
        "email": f"testuser_{ObjectId()}@test.com",
        "password": hash_password("TestPass123"),
        "role": "user",
        "avatar": None,
        "created_at": "2024-01-01T00:00:00+00:00",
    }
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    token = create_access_token(user_id)
    yield {"id": user_id, "email": user_doc["email"], "token": token, "name": user_doc["name"]}
    await db.users.delete_one({"_id": result.inserted_id})


@pytest.fixture
async def admin_user(setup_db):
    """Create an admin user and return user dict with auth cookie value."""
    db = get_db()
    user_doc = {
        "name": "Admin User",
        "email": f"admin_{ObjectId()}@test.com",
        "password": hash_password("AdminPass123"),
        "role": "admin",
        "avatar": None,
        "created_at": "2024-01-01T00:00:00+00:00",
    }
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    token = create_access_token(user_id)
    yield {"id": user_id, "email": user_doc["email"], "token": token, "name": user_doc["name"]}
    await db.users.delete_one({"_id": result.inserted_id})


@pytest.fixture
async def test_product(setup_db):
    """Create a test product and return its dict."""
    db = get_db()
    product_doc = {
        "name": "Test Product for Tests",
        "description": "A test product used in automated tests.",
        "price": 49.99,
        "category": "TestCategory",
        "stock": 100,
        "images": ["https://placehold.co/400x400"],
        "average_rating": 4.5,
        "review_count": 0,
        "created_at": "2024-01-01T00:00:00+00:00",
    }
    result = await db.products.insert_one(product_doc)
    product_doc["id"] = str(result.inserted_id)
    yield product_doc
    await db.products.delete_one({"_id": result.inserted_id})


def auth_cookies(token: str) -> dict:
    """Return cookies dict for authenticated requests."""
    return {"access_token": token}
