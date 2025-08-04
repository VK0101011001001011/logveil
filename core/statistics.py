from typing import Dict

class Statistics:
    """
    Manage redaction statistics.

    Attributes:
        stats (Dict[str, int]): Dictionary to store match counts by pattern.
    """

    def __init__(self, patterns: Dict[str, int]):
        self.stats = {key: 0 for key in patterns.keys()}

    def reset_stats(self):
        """
        Reset statistics for a new file or batch.
        """
        self.stats = {key: 0 for key in self.stats.keys()}

    def aggregate_stats(self, batch_stats: Dict[str, int]):
        """
        Aggregate statistics from multiple files.

        Args:
            batch_stats (Dict[str, int]): Statistics from a single file.
        """
        for key, value in batch_stats.items():
            self.stats[key] += value

    def get_stats(self) -> Dict[str, int]:
        """
        Get sanitization statistics.

        Returns:
            Dict[str, int]: A dictionary of match counts by pattern.
        """
        return self.stats

__all__ = ['Statistics']
