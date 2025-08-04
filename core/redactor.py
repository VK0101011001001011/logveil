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
    Sanitize a single line by replacing sensitive data with placeholders.

    Args:
        line (str): The input line to sanitize.

    Returns:
        Tuple[str, Dict[str, int]]: The sanitized line and a dictionary of match counts by pattern.

    Example:
        >>> sanitize_line("My email is test@example.com")
        ('My email is [REDACTED_EMAIL]', {'email': 1})
    """
    match_counts = {key: 0 for key in patterns.keys()}
    sanitized_line = line

    for label, regex in patterns.items():
        matches = regex.findall(sanitized_line)
        match_counts[label] += len(matches)
        sanitized_line = regex.sub(f"[REDACTED_{label.upper()}]", sanitized_line)

    return sanitized_line, match_counts

__all__ = ['sanitize_line']
