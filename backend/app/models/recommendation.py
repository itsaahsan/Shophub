"""Recommendation model for PostgreSQL."""

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Recommendation(BaseModel):
    """User recommendations based on purchase history."""

    __tablename__ = "recommendations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )
    purchased_product_ids: Mapped[list[str]] = mapped_column(JSONB, default=list)
