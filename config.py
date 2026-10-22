"""
Application configuration module.

Loads settings from environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    ENV = os.getenv("FLASK_ENV", "production")

    # Server settings
    PORT = int(os.getenv("PORT", 5000))

    # File upload settings
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10 MB default

    # Allowed extensions (empty list means allow all)
    ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "").split(",") if os.getenv("ALLOWED_EXTENSIONS") else []

    # Supported file categories
    SUPPORTED_CATEGORIES = [
        "image",
        "text",
        "document",
        "archive",
        "video",
        "audio",
        "other",
    ]
