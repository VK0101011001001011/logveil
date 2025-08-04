"""
Legacy compatibility module for LogVeil redaction functions.
Extracted from redactor.py to improve modularity and clarity.
"""

import re
from typing import Tuple, Dict

patterns = {
    "ip": re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"),
    "email": re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"),
    "uuid": re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b"),
    "sha256": re.compile(r"\b[a-fA-F0-9]{64}\b"),
    "md5": re.compile(r"\b[a-fA-F0-9]{32}\b"),
    "jwt": re.compile(r"\beyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\b"),
}

def sanitize_line(line: str) -> Tuple[str, Dict[str, int]]:
    """
    Legacy compatibility function for existing code.

    Args:
        line: Input line to sanitize

    Returns:
        Tuple of (sanitized_line, match_counts)
    """
    redacted_line = line
    match_counts = {}

    for name, pattern in patterns.items():
        matches = list(pattern.finditer(redacted_line))
        for match in matches:
            original_value = match.group()
            redacted_value = f"[REDACTED_{name.upper()}]"
            redacted_line = redacted_line.replace(original_value, redacted_value, 1)
            match_counts[name] = match_counts.get(name, 0) + 1

    return redacted_line, match_counts