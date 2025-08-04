#!/usr/bin/env python3
"""
LogVeil CLI Argument Parser
Enhanced argument parsing for the modular LogVeil system.
"""

import argparse
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_args():
    """
    Parse command-line arguments for the LogVeil log sanitizer.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="🔥 LogVeil 2.0: The Last Log Redactor You'll Ever Need",
        prog="logveil",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  logveil myapp.log                          # Basic redaction
  logveil *.log --profile nginx              # Use nginx profile  
  logveil logs/ --recursive --output clean/  # Process directory
  logveil app.log --trace trace.json         # Generate audit trail
  logveil --serve --port 8080                # Start API server
  logveil app.log --preview                  # Preview changes
  logveil app.log --engine rust              # Force specific engine
        """
    )

    # Input/Output
    parser.add_argument(
        "input",
        nargs="?",
        help="Path to input log file or directory to sanitize"
    )

    parser.add_argument(
        "-o", "--output",
        help="Path to output sanitized log file or directory",
        default=None
    )

    parser.add_argument(
        "--inplace",
        action="store_true",
        help="Overwrite input files with sanitized content"
    )

    parser.add_argument(
        "-r", "--recursive", 
        action="store_true",
        help="Process directories recursively"
    )

    # Redaction Configuration
    parser.add_argument(
        "-p", "--profile",
        help="Redaction profile to use (nginx, docker, cloudtrail, application, custom)",
        default=None
    )

    parser.add_argument(
        "--rules",
        help="Path to custom JSON/YAML file with redaction rules",
        default=None
    )

    parser.add_argument(
        "--entropy-threshold",
        type=float,
        help="Entropy threshold for secret detection (default: 4.2)",
        default=4.2
    )

    parser.add_argument(
        "--entropy-min-length",
        type=int,
        help="Minimum token length for entropy detection (default: 12)",
        default=12
    )

    parser.add_argument(
        "--disable-entropy",
        action="store_true",
        help="Disable entropy-based secret detection"
    )

    parser.add_argument(
        "--keys-to-redact",
        help="Comma-separated list of JSON/YAML key paths to redact (e.g., user.email,auth.token)",
        default=None
    )

    # Engine Selection
    parser.add_argument(
        "--engine",
        choices=["auto", "rust", "go", "python", "wasm"],
        default="auto",
        help="Execution engine to use (default: auto-detect optimal)"
    )

    # Output Modes
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Show side-by-side redacted line diffs without making changes"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform redaction analysis without writing files"
    )

    parser.add_argument(
        "--format",
        choices=["txt", "json", "yaml"],
        default="txt",
        help="Output format (default: txt)"
    )

    # Tracing and Auditing
    parser.add_argument(
        "--trace",
        metavar="FILE",
        help="Output detailed redaction trace to JSON file for audit trail"
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show redaction statistics summary"
    )

    # Server Mode
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start LogVeil API server for REST-based log sanitization"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for API server (default: 8080)"
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for API server (default: 127.0.0.1)"
    )

    # Processing Options
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Show progress bar during processing"
    )

    parser.add_argument(
        "--parallel",
        type=int,
        help="Number of parallel workers for processing (default: auto)",
        default=None
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        help="Chunk size for streaming large files (default: 1MB)",
        default=1024*1024
    )

    # Advanced Options
    parser.add_argument(
        "--plugins-dir",
        help="Directory containing custom redaction plugins",
        default=None
    )

    parser.add_argument(
        "--profiles-dir",
        help="Directory containing custom redaction profiles",
        default=None
    )

    parser.add_argument(
        "--config",
        help="Path to configuration file (JSON/YAML)",
        default=None
    )

    # Output Control
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress non-error output"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="count",
        default=0,
        help="Increase verbosity (use -vv for debug)"
    )

    # Safety Options
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite without confirmation"
    )

    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create backup files before modifying originals"
    )

    # Version and Help
    parser.add_argument(
        "--version",
        action="version",
        version="LogVeil 2.0.0"
    )

    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="List all available redaction profiles"
    )

    parser.add_argument(
        "--list-engines",
        action="store_true",
        help="List all available execution engines"
    )

    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run performance benchmark on sample data"
    )

    args = parser.parse_args()

    # Validation
    if not args.serve and not args.list_profiles and not args.list_engines and not args.benchmark and not args.input:
        parser.error("Input file/directory is required unless using --serve, --list-profiles, --list-engines, or --benchmark")

    if args.inplace and args.output:
        parser.error("Cannot use --inplace and --output together")

    if args.serve and args.input:
        parser.error("Cannot specify input when using --serve mode")

    if args.dry_run and args.inplace:
        parser.error("Cannot use --dry-run with --inplace")

    return args


def validate_args(args) -> bool:
    """
    Additional validation for parsed arguments.
    
    Args:
        args: Parsed arguments namespace
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Check input file/directory exists
    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            logger.error("Input path '%s' does not exist", args.input)
            return False
    
    # Check custom rules file exists
    if args.rules:
        rules_path = Path(args.rules)
        if not rules_path.exists():
            logger.error("Rules file '%s' does not exist", args.rules)
            return False
    
    # Check config file exists
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            logger.error("Config file '%s' does not exist", args.config)
            return False
    
    # Validate entropy threshold
    if args.entropy_threshold < 0 or args.entropy_threshold > 8:
        logger.error("Entropy threshold must be between 0 and 8, got %s", args.entropy_threshold)
        return False
    
    # Validate port range
    if args.port < 1 or args.port > 65535:
        logger.error("Port must be between 1 and 65535, got %s", args.port)
        return False
    
    return True


if __name__ == "__main__":
    # Test argument parsing
    test_args = [
        "test.log",
        "--profile", "nginx", 
        "--trace", "audit.json",
        "--stats",
        "--preview"
    ]
    
    import sys
    sys.argv = ["logveil"] + test_args
    
    args = parse_args()
    logger.info("Parsed args: %s", args)
    logger.info("Valid: %s", validate_args(args))
