#!/usr/bin/env python3
"""
Real functional tests for LogVeil entropy detection using stdlib unittest.
Production-grade testing without external dependencies.
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path to import logveil modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from logveil.core.sanitizer import SanitizerEngine


class TestEntropyDetection(unittest.TestCase):
    """Test cases for entropy-based secret detection."""

    def setUp(self):
        """Set up test environment."""
        self.engine = SanitizerEngine()
        self.engine.set_entropy_detection(True)
        self.engine.set_entropy_threshold(4.2)

    def test_entropy_detection(self):
        """Test detection of high-entropy strings."""
        line = "This is a test line with a secret key: abcdefghijklmnopqrstuvwxyz1234567890"
        sanitized_line = self.engine.sanitize_line(line)

        self.assertIn("[REDACTED_SECRET]", sanitized_line)
        self.assertEqual(self.engine.stats.get("secret", 0), 1)

    def test_no_entropy_detection_disabled(self):
        """Test that entropy detection can be disabled."""
        self.engine.set_entropy_detection(False)
        line = "This is a test line with a secret key: abcdefghijklmnopqrstuvwxyz1234567890"
        sanitized_line = self.engine.sanitize_line(line)

        self.assertNotIn("[REDACTED_SECRET]", sanitized_line)
        self.assertEqual(self.engine.stats.get("secret", 0), 0)

    def test_low_entropy_string(self):
        """Test that low-entropy strings are not flagged."""
        line = "This is a normal message with regular words"
        sanitized_line = self.engine.sanitize_line(line)
        
        # Low entropy string should not be redacted
        self.assertNotIn("[REDACTED_SECRET]", sanitized_line)
        self.assertEqual(sanitized_line, line)


if __name__ == "__main__":
    unittest.main(verbosity=2)
