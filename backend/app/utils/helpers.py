"""Shared utility functions."""

from bson import ObjectId
from datetime import datetime, timezone


def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document _id to string id."""
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


def serialize_docs(docs: list[dict]) -> list[dict]:
    """Serialize a list of MongoDB documents."""
    return [serialize_doc(d) for d in docs]


def to_object_id(id_str: str) -> ObjectId:
    """Convert string to ObjectId, raising ValueError if invalid."""
    if not ObjectId.is_valid(id_str):
        raise ValueError(f"Invalid ID: {id_str}")
    return ObjectId(id_str)


def utc_now() -> str:
    """Return current UTC time as ISO string."""
    return datetime.now(timezone.utc).isoformat()
