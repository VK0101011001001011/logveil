import json
from typing import List, Dict

def write_trace_log(trace_logs: List[Dict], trace_file: str):
    """
    Write trace logs to a file.

    Args:
        trace_logs (List[Dict]): List of trace log entries.
        trace_file (str): Path to the trace log file.

    Example:
        >>> write_trace_log([{"original": "test", "redacted": "[REDACTED]"}], "trace.json")
    """
    with open(trace_file, "a") as trace_out:
        json.dump(trace_logs, trace_out, indent=4)

__all__ = ['write_trace_log']
