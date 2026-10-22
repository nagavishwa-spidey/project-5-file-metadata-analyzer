"""
Unit tests for metadata extractor service.
"""

from services.metadata_extractor import extract_metadata, get_size_human, detect_category


def test_get_size_human():
    assert get_size_human(500) == "500 B"
    assert "KB" in get_size_human(2048)
    assert "MB" in get_size_human(5 * 1024 * 1024)


def test_detect_category():
    assert detect_category("image/png", ".png") == "image"
    assert detect_category("text/plain", ".txt") == "text"
    assert detect_category("application/zip", ".zip") == "archive"
    assert detect_category("application/pdf", ".pdf") == "document"


def test_extract_metadata_text(sample_text_file):
    meta = extract_metadata(sample_text_file, "sample.txt")
    assert meta["filename"] == "sample.txt"
    assert meta["extension"] == ".txt"
    assert "md5" in meta["hashes"]
    assert "sha256" in meta["hashes"]
    assert meta["category"] == "text"
    assert meta["is_text"] is True
    assert meta["analysis"]["line_count"] == 2


def test_extract_metadata_image(sample_image_file):
    meta = extract_metadata(sample_image_file, "pixel.png")
    assert meta["category"] == "image"
    assert meta["analysis"]["width"] == 2
    assert meta["analysis"]["height"] == 2
    assert meta["analysis"]["format"] == "PNG"
