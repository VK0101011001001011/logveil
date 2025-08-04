import math

def calculate_entropy(string: str) -> float:
    """
    Calculate Shannon entropy of a string.

    Args:
        string (str): Input string.

    Returns:
        float: Shannon entropy.

    Example:
        >>> calculate_entropy("hello")
        2.321928094887362
    """
    if not string:
        return 0

    frequency = {char: string.count(char) / len(string) for char in set(string)}
    entropy = -sum(freq * math.log2(freq) for freq in frequency.values())
    return entropy

__all__ = ['calculate_entropy']
