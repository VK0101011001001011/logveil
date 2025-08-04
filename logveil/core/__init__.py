"""
LogVeil Core Module
Core components for log sanitization and redaction.
"""

from .redactor import (
    RedactionEngine, 
    PatternRegistry, 
    EntropyDetector, 
    RedactionTrace, 
    RedactionStats, 
    RedactionReason
)

# Optional imports (may not be available without dependencies)
try:
    from .profiles import ProfileManager, RedactionProfile
except ImportError:
    ProfileManager = None
    RedactionProfile = None

try:
    from .structured import StructuredDataProcessor
except ImportError:
    StructuredDataProcessor = None

__all__ = [
    'RedactionEngine',
    'PatternRegistry', 
    'EntropyDetector',
    'RedactionTrace',
    'RedactionStats',
    'RedactionReason',
    'sanitize_line',
    'ProfileManager',
    'RedactionProfile',
    'StructuredDataProcessor'
]
