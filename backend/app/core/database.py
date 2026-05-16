"""PostgreSQL connection using SQLAlchemy async driver."""

from contextlib import asynccontextmanager
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all models."""
    pass


# Global engine and session maker
_engine: Optional[create_async_engine] = None
_session_maker: Optional[async_sessionmaker[AsyncSession]] = None


async def connect_db() -> async_sessionmaker[AsyncSession]:
    """Create and return an async session maker."""
    global _engine, _session_maker

    uri = settings.POSTGRESQL_URI
    if not uri:
        print("Warning: POSTGRESQL_URI is not set. Database-backed routes are unavailable.")
        _engine = None
        _session_maker = None
        return None

    _engine = create_async_engine(
        uri,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )

    # Verify connection
    try:
        async with _engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        print(f"Warning: PostgreSQL connection failed: {e}")
        await _engine.dispose()
        _engine = None
        _session_maker = None
        return None

    _session_maker = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    return _session_maker


async def close_db() -> None:
    """Close the PostgreSQL connection."""
    global _engine
    if _engine:
        await _engine.dispose()


@asynccontextmanager
async def get_session() -> AsyncSession:
    """Return a new database session. Use as: async with get_session() as session:"""
    global _session_maker
    if _session_maker is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    async with _session_maker() as session:
        yield session


async def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """Get the async session maker. Use with: async with get_session_maker()() as session:"""
    global _session_maker
    if _session_maker is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return _session_maker


async def create_tables() -> None:
    """Create all tables (for development)."""
    global _engine
    if _engine is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
