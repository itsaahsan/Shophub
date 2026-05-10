"""MongoDB connection using Motor async driver."""

import asyncio
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

# Global client instance
_mongo_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def connect_db() -> Optional[AsyncIOMotorDatabase]:
    """Create and return a Motor database bound to the current loop."""
    global _mongo_client, _db
    
    uri = settings.MONGODB_URI
    if not uri:
        print("Warning: MONGODB_URI is not set. Database-backed routes are unavailable.")
        _mongo_client = None
        _db = None
        return None

    db_name = settings.MONGODB_DB_NAME or "shophub"
    
    _mongo_client = AsyncIOMotorClient(
        uri,
        io_loop=asyncio.get_running_loop(),
        serverSelectionTimeoutMS=5000,
    )
    
    # Verify connection
    try:
        await _mongo_client.admin.command('ping')
    except Exception as e:
        print(f"Warning: MongoDB connection failed: {e}")
        _mongo_client.close()
        _mongo_client = None
        _db = None
        return None
    
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
