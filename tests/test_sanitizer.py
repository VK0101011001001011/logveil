import pytest
from core.sanitizer import sanitize_line

def test_ipv4():
    line = "User logged in from 192.168.1.1"
    sanitized, counts = sanitize_line(line)
    assert sanitized == "User logged in from [REDACTED_IP]"
    assert counts["ip"] == 1

def test_email():
    line = "Contact us at support@example.com"
    sanitized, counts = sanitize_line(line)
    assert sanitized == "Contact us at [REDACTED_EMAIL]"
    assert counts["email"] == 1

def test_uuid():
    line = "Generated UUID: 550e8400-e29b-41d4-a716-446655440000"
    sanitized, counts = sanitize_line(line)
    assert sanitized == "Generated UUID: [REDACTED_UUID]"
    assert counts["uuid"] == 1

def test_sha256():
    line = "Transaction hash: a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"
    sanitized, counts = sanitize_line(line)
    assert sanitized == "Transaction hash: [REDACTED_SHA256]"
    assert counts["sha256"] == 1

def test_md5():
    line = "MD5 checksum: 5d41402abc4b2a76b9719d911017c592"
    sanitized, counts = sanitize_line(line)
    assert sanitized == "MD5 checksum: [REDACTED_MD5]"
    assert counts["md5"] == 1

def test_jwt():
    line = "JWT token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    sanitized, counts = sanitize_line(line)
    assert sanitized == "JWT token: [REDACTED_JWT]"
    assert counts["jwt"] == 1
