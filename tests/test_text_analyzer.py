"""
Unit tests for text file analyzer service.
"""

from services.text_analyzer import analyze_text


def test_analyze_english_text(sample_text_file):
    res = analyze_text(sample_text_file)
    assert res is not None
    assert res["line_count"] == 2
    assert res["word_count"] > 0
    assert res["char_count"] > 0
    assert res["is_empty"] is False


def test_analyze_empty_file():
    res = analyze_text(b"")
    assert res["is_empty"] is True
    assert res["line_count"] == 0
