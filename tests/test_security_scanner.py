"""
Unit tests for security scanner service.
"""

from services.security_scanner import scan_file


def test_scan_safe_text_file():
    res = scan_file(b"This is normal safe text", "document.txt", "text/plain")
    assert res["risk_level"] == "safe"
    assert len(res["warnings"]) == 0


def test_scan_executable_extension():
    res = scan_file(b"MZ\x90...", "malware.exe", "application/octet-stream")
    assert res["risk_level"] == "high"
    assert any("executable" in w.lower() for w in res["warnings"])


def test_scan_double_extension():
    res = scan_file(b"dummy", "invoice.pdf.exe", "application/octet-stream")
    assert res["risk_level"] == "high"
    assert any("double extension" in w.lower() for w in res["warnings"])


def test_scan_embedded_script_tag():
    res = scan_file(b"<svg><script>alert(1)</script></svg>", "image.svg", "image/svg+xml")
    assert any("script" in w.lower() for w in res["warnings"])
