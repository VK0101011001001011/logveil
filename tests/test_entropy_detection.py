import unittest
from core.sanitizer import SanitizerEngine

class TestEntropyDetection(unittest.TestCase):
    def setUp(self):
        self.engine = SanitizerEngine()
        self.engine.enable_entropy_detection(True)
        self.engine.set_entropy_threshold(4.2)

    def test_entropy_detection(self):
        line = "This is a test line with a secret key: abcdefghijklmnopqrstuvwxyz1234567890"
        sanitized_line = self.engine.sanitize_line(line)

        self.assertIn("[REDACTED_SECRET]", sanitized_line)
        self.assertEqual(self.engine.stats.get("secret", 0), 1)

    def test_no_entropy_detection(self):
        self.engine.enable_entropy_detection(False)
        line = "This is a test line with a secret key: abcdefghijklmnopqrstuvwxyz1234567890"
        sanitized_line = self.engine.sanitize_line(line)

        self.assertNotIn("[REDACTED_SECRET]", sanitized_line)

if __name__ == "__main__":
    unittest.main()
