"""
File utility functions.

Provides MIME type detection, extension extraction, and size validation
helpers used throughout the application.
"""

import mimetypes
import os


# Initialize mimetypes database
mimetypes.init()

# Additional MIME type mappings not always in the default database
EXTRA_MIME_TYPES = {
    ".md": "text/markdown",
    ".yaml": "text/yaml",
    ".yml": "text/yaml",
    ".json": "application/json",
    ".csv": "text/csv",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
    ".ts": "application/typescript",
    ".tsx": "application/typescript",
    ".jsx": "application/javascript",
    ".wasm": "application/wasm",
}


def get_mime_type(file_bytes: bytes, filename: str) -> str:
    """
    Detect MIME type of a file using filename and content inspection.

    Falls back to mimetypes module (filename-based) since python-magic
    may not be available on all platforms.

    Args:
        file_bytes: Raw bytes of the file.
        filename: Original filename.

    Returns:
        MIME type string, e.g. 'text/plain'.
    """
    # Try filename-based detection first
    ext = get_extension(filename)

    # Check our custom mappings
    if ext in EXTRA_MIME_TYPES:
        return EXTRA_MIME_TYPES[ext]

    # Use mimetypes module
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type:
        return mime_type

    # Content-based fallback: check for common magic bytes
    mime_from_content = _detect_from_content(file_bytes)
    if mime_from_content:
        return mime_from_content

    return "application/octet-stream"


def _detect_from_content(file_bytes: bytes) -> str | None:
    """
    Detect MIME type from file content magic bytes.

    Args:
        file_bytes: Raw bytes of the file.

    Returns:
        MIME type string if detected, None otherwise.
    """
    if not file_bytes:
        return None

    # Common magic byte signatures
    signatures = {
        b"\x89PNG\r\n\x1a\n": "image/png",
        b"\xff\xd8\xff": "image/jpeg",
        b"GIF87a": "image/gif",
        b"GIF89a": "image/gif",
        b"PK\x03\x04": "application/zip",
        b"%PDF": "application/pdf",
        b"\x1f\x8b": "application/gzip",
        b"RIFF": "application/octet-stream",  # Could be WAV, AVI, etc.
        b"\x00\x00\x01\x00": "image/x-icon",
    }

    for magic, mime in signatures.items():
        if file_bytes[:len(magic)] == magic:
            return mime

    return None


def get_extension(filename: str) -> str:
    """
    Extract and normalize the file extension.

    Args:
        filename: Original filename.

    Returns:
        Lowercase extension with dot (e.g., '.txt'), or empty string.
    """
    if not filename:
        return ""
    _, ext = os.path.splitext(filename)
    return ext.lower()


def is_allowed_size(size: int, max_size: int) -> bool:
    """
    Check if a file size is within the allowed limit.

    Args:
        size: File size in bytes.
        max_size: Maximum allowed size in bytes.

    Returns:
        True if size is within the limit.
    """
    return 0 <= size <= max_size
