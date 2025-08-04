import re
import json
from typing import Dict, Tuple

# Global dictionary of compiled regex patterns and their labels
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
    """
    match_counts = {key: 0 for key in patterns.keys()}
    sanitized_line = line

    for label, regex in patterns.items():
        matches = regex.findall(sanitized_line)
        match_counts[label] += len(matches)
        sanitized_line = regex.sub(f"[REDACTED_{label.upper()}]", sanitized_line)

    return sanitized_line, match_counts

def load_custom_patterns(json_path: str) -> Dict[str, re.Pattern]:
    """
    Load custom regex patterns from a JSON file.

    Args:
        json_path (str): Path to the JSON file.

    Returns:
        Dict[str, re.Pattern]: A dictionary of compiled regex patterns.

    Raises:
        ValueError: If the JSON file format is invalid.
    """
    try:
        with open(json_path, "r", encoding="utf-8") as file:
            user_patterns = json.load(file)

        if not isinstance(user_patterns, dict):
            raise ValueError("Custom patterns must be a dictionary.")

        compiled_patterns = {}
        for name, pattern in user_patterns.items():
            if not isinstance(name, str) or not isinstance(pattern, str):
                raise ValueError("Each pattern must have a string name and a string regex.")
            compiled_patterns[name] = re.compile(pattern)

        return compiled_patterns

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON file: {e}")

def merge_patterns(default_patterns: Dict[str, re.Pattern], custom_patterns: Dict[str, re.Pattern]) -> Dict[str, re.Pattern]:
    """
    Merge default patterns with custom patterns, giving priority to custom patterns.

    Args:
        default_patterns (Dict[str, re.Pattern]): Default regex patterns.
        custom_patterns (Dict[str, re.Pattern]): Custom regex patterns.

    Returns:
        Dict[str, re.Pattern]: Merged regex patterns.
    """
    merged = default_patterns.copy()
    merged.update(custom_patterns)
    return merged

class SanitizerEngine:
    def __init__(self):
        self.patterns = patterns
        self.stats = {key: 0 for key in self.patterns.keys()}

    def sanitize_line(self, line: str) -> str:
        """
        Sanitize a single line by replacing sensitive data with placeholders.

        Args:
            line (str): The input line to sanitize.

        Returns:
            str: The sanitized line.
        """
        sanitized_line = line

        for label, regex in self.patterns.items():
            matches = regex.findall(sanitized_line)
            self.stats[label] += len(matches)
            sanitized_line = regex.sub(f"[REDACTED_{label.upper()}]", sanitized_line)

        return sanitized_line

    def load_patterns(self, custom_path: str):
        """
        Load custom regex patterns from a JSON file and merge them with default patterns.

        Args:
            custom_path (str): Path to the JSON file.

        Raises:
            ValueError: If the JSON file format is invalid.
        """
        custom_patterns = load_custom_patterns(custom_path)
        self.patterns = merge_patterns(self.patterns, custom_patterns)

    def get_stats(self) -> Dict[str, int]:
        """
        Get sanitization statistics.

        Returns:
            Dict[str, int]: A dictionary of match counts by pattern.
        """
        return self.stats

    def sanitize_lines(self, lines: list) -> list:
        """
        Sanitize multiple lines concurrently.

        Args:
            lines (list): List of input lines to sanitize.

        Returns:
            list: List of sanitized lines.
        """
        from concurrent.futures import ThreadPoolExecutor

        def sanitize(line):
            return self.sanitize_line(line)

        with ThreadPoolExecutor() as executor:
            sanitized_lines = list(executor.map(sanitize, lines))

        return sanitized_lines

__all__ = ['SanitizerEngine']
