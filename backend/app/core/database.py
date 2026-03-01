"""MongoDB connection using Motor async driver."""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

# Global client instance
_mongo_client: AsyncIOMotorClient = None  # type: ignore
_db: AsyncIOMotorDatabase = None  # type: ignore


async def connect_db() -> AsyncIOMotorDatabase:
    """Create and return a Motor database bound to the current loop."""
    global _mongo_client, _db
    
    uri = settings.MONGODB_URI or "mongodb://localhost:27017"
    db_name = settings.MONGODB_DB_NAME or "shophub"
    
    _mongo_client = AsyncIOMotorClient(uri, io_loop=asyncio.get_running_loop())
    
    # Verify connection
    try:
        await _mongo_client.admin.command('ping')
    except Exception as e:
        print(f"Warning: MongoDB connection failed: {e}")
    
    _db = _mongo_client[db_name]
    return _db


async def close_db() -> None:
    """Close the MongoDB connection."""
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()


def get_db() -> AsyncIOMotorDatabase:
    """Return the cached database instance."""
    global _db
    if _db is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return _db
