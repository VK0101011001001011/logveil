#!/usr/bin/env python3
"""
Real functional tests for LogVeil CLI agent using stdlib unittest.
Production-grade integration testing without external dependencies.
"""

import unittest
import subprocess
import os
import json
import sys
from pathlib import Path

# Add parent directory to path to import logveil modules
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestLogVeilAgent(unittest.TestCase):
    """Integration tests for the LogVeil CLI agent."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(__file__).parent.parent
        self.input_file = self.test_dir / "sample_log.txt"
        self.output_file = self.test_dir / "test_output.log"
        self.agent_script = self.test_dir / "logveil" / "cli" / "logveil_agent.py"

    def tearDown(self):
        """Clean up test files."""
        if self.output_file.exists():
            self.output_file.unlink()

    def test_agent_execution(self):
        """Test that the agent runs without errors."""
        if not self.input_file.exists():
            self.skipTest("Sample log file not found")
        
        # Run logveil-agent.py
        result = subprocess.run([
            sys.executable, 
            str(self.agent_script), 
            str(self.input_file), 
            "--output", str(self.output_file), 
            "--profile", "nginx"
        ], capture_output=True, text=True)

        # Check that command succeeded
        self.assertEqual(result.returncode, 0, f"Agent failed: {result.stderr}")
        
        # Assert output file exists
        self.assertTrue(self.output_file.exists(), "Output file not created")

    def test_output_format(self):
        """Test that output is valid JSON with expected structure."""
        if not self.input_file.exists():
            self.skipTest("Sample log file not found")
            
        # Run agent first
        subprocess.run([
            sys.executable, 
            str(self.agent_script), 
            str(self.input_file), 
            "--output", str(self.output_file), 
            "--profile", "nginx"
        ], check=True)

        # Validate JSON output
        with open(self.output_file, "r") as outfile:
            try:
                output_data = json.load(outfile)
            except json.JSONDecodeError:
                self.fail("Output file is not valid JSON")

        # Check required fields
        self.assertIn("file", output_data, "Missing 'file' in output JSON")
        self.assertIn("sanitized_lines", output_data, "Missing 'sanitized_lines' in output JSON")


if __name__ == "__main__":
    unittest.main(verbosity=2)
    assert "summary" in output_data, "Missing 'summary' in output JSON"
    assert "timestamp" in output_data, "Missing 'timestamp' in output JSON"

    print("Functional test passed!")

if __name__ == "__main__":
    test_logveil_agent()
