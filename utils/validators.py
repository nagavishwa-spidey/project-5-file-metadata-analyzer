"""
Input validation utilities.

Validates file uploads, filenames, and other user inputs to ensure
safe and correct processing.
"""

import os
import re
from config import Config


def validate_upload(file) -> tuple:
    """
    Validate a file upload object from Flask.

    Args:
        file: Flask FileStorage object.

    Returns:
        Tuple of (is_valid: bool, error_message: str | None).
    """
    # Check file exists
    if file is None:
        return False, "No file provided"

    # Check file has a filename
    if not file.filename or file.filename.strip() == "":
        return False, "No filename provided"

    # Read content to check size
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)

    if size == 0:
        return False, "File is empty"

    if size > Config.MAX_FILE_SIZE:
        max_mb = Config.MAX_FILE_SIZE / (1024 * 1024)
        return False, f"File exceeds maximum size of {max_mb:.0f} MB"

    return True, None


def validate_filename(filename: str) -> str:
    """
    Sanitize a filename by removing dangerous characters.

    Keeps alphanumeric characters, dots, hyphens, underscores, and spaces.
    Preserves the original extension.

    Args:
        filename: Original filename string.

    Returns:
        Sanitized filename string.
    """
    if not filename:
        return "unnamed_file"

    # Remove path components
    filename = os.path.basename(filename)

    # Replace dangerous characters but keep dots, hyphens, underscores, spaces
    sanitized = re.sub(r'[^\w\s\-.]', '', filename)

    # Remove leading/trailing whitespace and dots (prevent hidden files)
    sanitized = sanitized.strip().strip(".")

    # Collapse multiple spaces
    sanitized = re.sub(r'\s+', ' ', sanitized)

    if not sanitized:
        return "unnamed_file"

    return sanitized
