import glob
import json
import yaml
import re
from typing import Dict

def load_custom_patterns(json_path: str) -> Dict[str, re.Pattern]:
    """
    Load custom regex patterns from a JSON file.

    Args:
        json_path (str): Path to the JSON file.

    Returns:
        Dict[str, re.Pattern]: A dictionary of compiled regex patterns.

    Example:
        >>> load_custom_patterns("patterns.json")
        {"email": re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")}

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

def load_redaction_policy(policy_path: str):
    """
    Load redaction rules from a YAML policy file.

    Args:
        policy_path (str): Path to the YAML policy file.

    Returns:
        dict: Redaction rules.

    Raises:
        ValueError: If the policy file format is invalid.
    """
    try:
        with open(policy_path, "r", encoding="utf-8") as file:
            policy_data = yaml.safe_load(file)

        if not isinstance(policy_data, dict) or "rules" not in policy_data:
            raise ValueError("Invalid policy format")

        return policy_data["rules"]

    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML file: {e}")

__all__ = ['load_custom_patterns', 'load_redaction_policy']
