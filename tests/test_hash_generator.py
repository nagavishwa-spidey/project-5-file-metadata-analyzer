"""
Unit tests for cryptographic hash generator.
"""

from services.hash_generator import generate_md5, generate_sha256, generate_all_hashes


def test_hash_md5():
    data = b"hello cloud"
    assert generate_md5(data) == "a30d495f1f38ebf6641f0dc0b9362b10"


def test_hash_sha256():
    data = b"hello cloud"
    assert generate_sha256(data) == "68dfdc1d0305198f4347e2c7f2427e71f2179edfe44c6603d28bab67fbbea745"


def test_generate_all_hashes():
    hashes = generate_all_hashes(b"data")
    assert "md5" in hashes
    assert "sha256" in hashes
