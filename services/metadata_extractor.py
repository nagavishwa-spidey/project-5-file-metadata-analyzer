"""
Core Metadata Extractor Service for Cloud File Metadata Analyzer.

Orchestrates hash generation, MIME type detection, category classification,
security scanning, and domain-specific content analysis (image EXIF / text stats).
"""

import os
from utils.file_utils import get_mime_type, get_extension
from services.hash_generator import generate_all_hashes
from services.image_analyzer import analyze_image
from services.text_analyzer import analyze_text
from services.security_scanner import scan_file


def get_size_human(size_bytes: int) -> str:
    """Format byte size into human-readable representation."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def detect_category(mime_type: str, extension: str) -> str:
    """
    Categorize file into one of:
    'image', 'text', 'document', 'archive', 'video', 'audio', 'other'
    """
    mime_type = mime_type.lower()
    ext = extension.lower().lstrip('.')

    if mime_type.startswith('image/') or ext in {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg'}:
        return 'image'
    if mime_type.startswith('text/') or ext in {'txt', 'md', 'csv', 'tsv', 'json', 'xml', 'html', 'css', 'js', 'py'}:
        return 'text'
    if mime_type.startswith('video/') or ext in {'mp4', 'mkv', 'avi', 'mov', 'webm'}:
        return 'video'
    if mime_type.startswith('audio/') or ext in {'mp3', 'wav', 'ogg', 'flac', 'aac'}:
        return 'audio'
    if ext in {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'odt'}:
        return 'document'
    if ext in {'zip', 'tar', 'gz', 'bz2', '7z', 'rar'} or 'zip' in mime_type or 'tar' in mime_type:
        return 'archive'

    return 'other'


def extract_metadata(file_bytes: bytes, filename: str) -> dict:
    """
    Extract comprehensive metadata dictionary for an uploaded file.
    """
    size_bytes = len(file_bytes)
    size_human = get_size_human(size_bytes)
    extension = get_extension(filename)
    mime_type = get_mime_type(file_bytes, filename)
    category = detect_category(mime_type, extension)
    hashes = generate_all_hashes(file_bytes)
    security = scan_file(file_bytes, filename, mime_type)

    analysis = {}
    is_text = False

    if category == 'image':
        img_info = analyze_image(file_bytes)
        if img_info:
            analysis = img_info
    elif category == 'text' or mime_type.startswith('text/') or extension in {'.txt', '.csv', '.json', '.md'}:
        txt_info = analyze_text(file_bytes)
        if txt_info:
            analysis = txt_info
            is_text = True
    else:
        # Check if text analysis works anyway
        txt_info = analyze_text(file_bytes)
        if txt_info and not txt_info.get('is_empty'):
            analysis = txt_info
            is_text = True

    return {
        "filename": filename,
        "extension": extension,
        "mime_type": mime_type,
        "size_bytes": size_bytes,
        "size_human": size_human,
        "hashes": hashes,
        "category": category,
        "is_text": is_text,
        "security": security,
        "analysis": analysis
    }
