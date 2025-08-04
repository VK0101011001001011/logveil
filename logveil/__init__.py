"""
LogVeil - Production-grade log sanitization and redaction engine.

LogVeil is a comprehensive log sanitization toolkit that provides intelligent
detection and redaction of sensitive data in log files. It supports multiple
processing engines, custom profiles, and various output formats.

Key Features:
- Multi-engine processing (Python, Rust, hybrid)
- Intelligent entropy-based detection
- Customizable redaction profiles  
- API server mode
- CLI and programmatic interfaces
- High-performance batch processing

Author: LogVeil Team
License: MIT
"""

__version__ = "2.0.0"
__author__ = "LogVeil Team"
__license__ = "MIT"

# Public API exports
from .core.redactor import RedactionEngine
from .core.profiles import ProfileManager
from .core.sanitizer import SanitizerEngine
from .logveil_types.models import RedactionResult, TraceItem

__all__ = [
    "RedactionEngine",
    "ProfileManager", 
    "SanitizerEngine",
    "RedactionResult",
    "TraceItem",
]
