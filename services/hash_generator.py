"""
File hashing service.

Generates MD5 and SHA256 hashes for uploaded files, processing in chunks
for memory efficiency — a pattern commonly used in cloud storage systems
for integrity verification.
"""

import hashlib

# Chunk size for processing large files (8 KB)
CHUNK_SIZE = 8192


def generate_md5(file_bytes: bytes) -> str:
    """
    Generate MD5 hex digest for file bytes.

    Processes the file in chunks for memory efficiency.

    Args:
        file_bytes: Raw bytes of the file.

    Returns:
        MD5 hex digest string.
    """
    hasher = hashlib.md5()
    offset = 0
    while offset < len(file_bytes):
        chunk = file_bytes[offset : offset + CHUNK_SIZE]
        hasher.update(chunk)
        offset += CHUNK_SIZE
    return hasher.hexdigest()


def generate_sha256(file_bytes: bytes) -> str:
    """
    Generate SHA256 hex digest for file bytes.

    Processes the file in chunks for memory efficiency.

    Args:
        file_bytes: Raw bytes of the file.

    Returns:
        SHA256 hex digest string.
    """
    hasher = hashlib.sha256()
    offset = 0
    while offset < len(file_bytes):
        chunk = file_bytes[offset : offset + CHUNK_SIZE]
        hasher.update(chunk)
        offset += CHUNK_SIZE
    return hasher.hexdigest()


def generate_all_hashes(file_bytes: bytes) -> dict:
    """
    Generate all supported hashes for file bytes in a single pass.

    Args:
        file_bytes: Raw bytes of the file.

    Returns:
        Dictionary with 'md5' and 'sha256' hex digests.
    """
    md5_hasher = hashlib.md5()
    sha256_hasher = hashlib.sha256()

    offset = 0
    while offset < len(file_bytes):
        chunk = file_bytes[offset : offset + CHUNK_SIZE]
        md5_hasher.update(chunk)
        sha256_hasher.update(chunk)
        offset += CHUNK_SIZE

    return {
        "md5": md5_hasher.hexdigest(),
        "sha256": sha256_hasher.hexdigest(),
    }
