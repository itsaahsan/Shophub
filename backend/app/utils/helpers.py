"""Shared utility functions."""

import json
import uuid
from datetime import datetime, timezone


def serialize_doc(doc: dict) -> dict:
    """Convert SQLAlchemy model to dict with string id."""
    if doc is None:
        return doc
    if hasattr(doc, "__dict__"):
        doc = doc.__dict__
    if "id" in doc and isinstance(doc["id"], uuid.UUID):
        doc["id"] = str(doc["id"])
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


def serialize_docs(docs: list) -> list[dict]:
    """Serialize a list of SQLAlchemy models."""
    return [serialize_doc(d) for d in docs]


def to_uuid(id_str: str) -> uuid.UUID:
    """Convert string to UUID, raising ValueError if invalid."""
    try:
        return uuid.UUID(id_str)
    except ValueError:
        raise ValueError(f"Invalid ID: {id_str}")


def utc_now() -> str:
    """Return current UTC time as ISO string."""
    return datetime.now(timezone.utc).isoformat()


def parse_json(json_str: str) -> list:
    """Parse JSON string to list."""
    if not json_str:
        return []
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return []


def to_json(data: list) -> str:
    """Convert list to JSON string."""
    return json.dumps(data)