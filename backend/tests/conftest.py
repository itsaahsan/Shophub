"""Shared test fixtures for pytest."""

import asyncio
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.database import get_session, connect_db, close_db, create_tables
from app.core.redis import connect_redis, close_redis
from app.core.security import hash_password, create_access_token
from app.models.user import User, UserRole
from app.models.product import Product


@pytest.fixture(scope="session")
def event_loop():
    """Create and set an event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_db():
    """Connect to test database once per session."""
    await connect_db()
    await create_tables() # Ensure tables exist
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
    async with get_session() as session:
        user = User(
            name="Test User",
            email=f"testuser_{uuid.uuid4()}@test.com",
            password=hash_password("TestPass123"),
            role=UserRole.USER.value,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        user_id = str(user.id)
        token = create_access_token(user_id)
        user_dict = {"id": user_id, "email": user.email, "token": token, "name": user.name}
        
    yield user_dict
    
    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalar_one_or_none()
        if user:
            await session.delete(user)
            await session.commit()


@pytest.fixture
async def admin_user(setup_db):
    """Create an admin user and return user dict with auth cookie value."""
    async with get_session() as session:
        user = User(
            name="Admin User",
            email=f"admin_{uuid.uuid4()}@test.com",
            password=hash_password("AdminPass123"),
            role=UserRole.ADMIN.value,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        user_id = str(user.id)
        token = create_access_token(user_id)
        user_dict = {"id": user_id, "email": user.email, "token": token, "name": user.name}
        
    yield user_dict
    
    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalar_one_or_none()
        if user:
            await session.delete(user)
            await session.commit()


@pytest.fixture
async def test_product(setup_db):
    """Create a test product and return its dict."""
    async with get_session() as session:
        product = Product(
            name="Test Product for Tests",
            description="A test product used in automated tests.",
            price=49.99,
            category="TestCategory",
            stock=100,
            images=[],
            average_rating=4.5,
            review_count=0,
        )
        session.add(product)
        await session.commit()
        await session.refresh(product)
        
        product_id = str(product.id)
        product_dict = {
            "id": product_id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "category": product.category,
            "stock": product.stock,
        }
        
    yield product_dict
    
    async with get_session() as session:
        result = await session.execute(select(Product).where(Product.id == uuid.UUID(product_id)))
        product = result.scalar_one_or_none()
        if product:
            await session.delete(product)
            await session.commit()


def auth_cookies(token: str) -> dict:
    """Return cookies dict for authenticated requests."""
    return {"access_token": token}


from sqlalchemy import select
