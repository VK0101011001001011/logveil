#!/usr/bin/env python3
"""
Real functional tests for LogVeil sanitizer using stdlib unittest.
Production-grade testing without external dependencies.
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path to import logveil modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from logveil.core.sanitizer import sanitize_line


class TestSanitizer(unittest.TestCase):
    """Test cases for core sanitization functionality."""

    def test_ipv4_redaction(self):
        """Test IPv4 address redaction."""
        line = "User logged in from 192.168.1.1"
        sanitized, counts = sanitize_line(line)
        self.assertEqual(sanitized, "User logged in from [REDACTED_IP]")
        self.assertEqual(counts["ip"], 1)

    def test_email_redaction(self):
        """Test email address redaction."""
        line = "Contact us at support@example.com"
        sanitized, counts = sanitize_line(line)
        self.assertEqual(sanitized, "Contact us at [REDACTED_EMAIL]")
    def test_multiple_patterns(self):
        """Test multiple pattern types in single line."""
        line = "Error from 10.0.0.1: user user@example.com failed login"
        sanitized, counts = sanitize_line(line)
        expected = "Error from [REDACTED_IP]: user [REDACTED_EMAIL] failed login"
        self.assertEqual(sanitized, expected)
        self.assertEqual(counts["ip"], 1)
        self.assertEqual(counts["email"], 1)

    def test_no_matches(self):
        """Test line with no sensitive data."""
        line = "Normal log message with no sensitive content"
        sanitized, counts = sanitize_line(line)
        self.assertEqual(sanitized, line)
        # Sanitizer returns all counters initialized to 0
        self.assertTrue(all(count == 0 for count in counts.values()))


if __name__ == "__main__":
    unittest.main(verbosity=2)

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
