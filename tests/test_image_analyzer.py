"""
Unit tests for image analyzer service.
"""

from services.image_analyzer import analyze_image


def test_analyze_valid_png(sample_image_file):
    res = analyze_image(sample_image_file)
    assert res is not None
    assert res["width"] == 2
    assert res["height"] == 2
    assert res["format"] == "PNG"


def test_analyze_non_image():
    res = analyze_image(b"just random text content")
    assert res is None
