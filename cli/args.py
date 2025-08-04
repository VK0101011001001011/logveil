import argparse

def parse_args():
    """
    Parse command-line arguments for the log sanitizer tool.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="LogVeil: A fast, production-grade log sanitizer",
        prog="logveil"
    )

    parser.add_argument(
        "input",
        help="Path to the input log file to sanitize"
    )

    parser.add_argument(
        "-o", "--output",
        help="Path to the output sanitized log file (default: stdout)",
        default=None
    )

    parser.add_argument(
        "--inplace",
        action="store_true",
        help="Overwrite the input file with sanitized content"
    )

    parser.add_argument(
        "--preview",
        action="store_true",
        help="Show side-by-side redacted line diffs"
    )

    parser.add_argument(
        "--progress",
        action="store_true",
        help="Show a progress bar during sanitization"
    )

    parser.add_argument(
        "--summary",
        action="store_true",
        help="Output a summary of redacted items"
    )

    parser.add_argument(
        "--rules",
        help="Path to a JSON file with custom regex patterns",
        default=None
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without writing files"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite without confirmation"
    )

    parser.add_argument(
        "--format",
        choices=["txt", "json"],
        default="txt",
        help="Output format: txt (default) or json"
    )

    return parser.parse_args()
