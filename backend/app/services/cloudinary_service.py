"""Cloudinary image upload service."""

import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from app.core.config import settings


def configure_cloudinary() -> None:
    """Initialize Cloudinary configuration."""
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )


async def upload_image(file: UploadFile) -> str:
    """Upload an image file to Cloudinary and return the secure URL."""
    # Reading file content synchronously is fine for this task context
    # or using wrap in run_in_executor if needed, but standard library often sufficient
    result = cloudinary.uploader.upload(
        file.file,
        folder="shop-hub/products",
        resource_type="image",
    )
    return result.get("secure_url")
