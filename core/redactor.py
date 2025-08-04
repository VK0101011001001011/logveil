"""
LogVeil Core Redaction Engine
High-performance, modular redaction engine with pluggable intelligence.
"""

import re
import math
import json
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path


class RedactionReason(Enum):
    """Reasons for redaction."""
    PATTERN_MATCH = "pattern_match"
    ENTROPY_DETECTION = "entropy_detection"
    CUSTOM_RULE = "custom_rule"
    PLUGIN_DETECTION = "plugin_detection"


@dataclass
class RedactionTrace:
    """Trace information for a redaction operation."""
    original_value: str
    redacted_value: str
    reason: RedactionReason
    pattern_name: Optional[str]
    line_number: Optional[int]
    file_path: Optional[str]
    entropy_score: Optional[float] = None
    confidence: float = 1.0


@dataclass
class RedactionStats:
    """Statistics for redaction operations."""
    total_lines_processed: int = 0
    total_redactions: int = 0
    redactions_by_pattern: Dict[str, int] = None
    entropy_detections: int = 0
    processing_time_ms: float = 0.0
    
    def __post_init__(self):
        if self.redactions_by_pattern is None:
            self.redactions_by_pattern = {}


class PatternRegistry:
    """Registry for redaction patterns."""
    
    DEFAULT_PATTERNS = {
        "ip_address": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
        "email": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
        "uuid": r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b",
        "sha256": r"\b[a-fA-F0-9]{64}\b",
        "sha1": r"\b[a-fA-F0-9]{40}\b",
        "md5": r"\b[a-fA-F0-9]{32}\b",
        "jwt": r"\beyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\b",
        "aws_access_key": r"\bAKIA[0-9A-Z]{16}\b",
        "aws_secret_key": r"\b[0-9a-zA-Z/+]{40}\b",
        "credit_card": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "phone": r"\b\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b",
        "api_key": r"\b[a-zA-Z0-9]{32,}\b",
        "bearer_token": r"\bBearer\s+[a-zA-Z0-9_-]+\b",
        "password": r"(?i)(password|passwd|pwd)[\s=:]+[^\s]+",
        "private_key": r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----",
    }
    
    def __init__(self):
        self.patterns: Dict[str, re.Pattern] = {}
        self.load_default_patterns()
    
    def load_default_patterns(self):
        """Load default redaction patterns."""
        for name, pattern in self.DEFAULT_PATTERNS.items():
            self.patterns[name] = re.compile(pattern, re.IGNORECASE)
    
    def add_pattern(self, name: str, pattern: str, flags: int = re.IGNORECASE):
        """Add a custom pattern."""
        self.patterns[name] = re.compile(pattern, flags)
    
    def remove_pattern(self, name: str):
        """Remove a pattern."""
        self.patterns.pop(name, None)
    
    def load_from_file(self, file_path: Union[str, Path]):
        """Load patterns from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            pattern_data = json.load(f)
        
        for name, pattern_info in pattern_data.items():
            if isinstance(pattern_info, str):
                self.add_pattern(name, pattern_info)
            elif isinstance(pattern_info, dict):
                pattern = pattern_info.get("pattern", "")
                flags = pattern_info.get("flags", re.IGNORECASE)
                self.add_pattern(name, pattern, flags)


class EntropyDetector:
    """Shannon entropy-based secret detection."""
    
    def __init__(self, threshold: float = 4.2, min_length: int = 12):
        self.threshold = threshold
        self.min_length = min_length
    
    def calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of a string."""
        if not text:
            return 0.0
        
        # Count character frequencies
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        length = len(text)
        entropy = 0.0
        for count in char_counts.values():
            probability = count / length
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def is_high_entropy(self, text: str) -> Tuple[bool, float]:
        """Check if text has high entropy indicating a potential secret."""
        if len(text) < self.min_length:
            return False, 0.0
        
        entropy = self.calculate_entropy(text)
        return entropy >= self.threshold, entropy
    
    def detect_secrets_in_line(self, line: str) -> List[Tuple[str, float]]:
        """Detect potential secrets in a line using entropy analysis."""
        secrets = []
        
        # Split line into tokens
        tokens = re.findall(r'\S+', line)
        
        for token in tokens:
            # Clean token (remove common prefixes/suffixes)
            clean_token = re.sub(r'^["\'\[\(]|["\'\]\)]$', '', token)
            clean_token = re.sub(r'[,;:]$', '', clean_token)
            
            is_secret, entropy = self.is_high_entropy(clean_token)
            if is_secret:
                secrets.append((token, entropy))
        
        return secrets


class RedactionEngine:
    """Core redaction engine with pattern matching and entropy detection."""
    
    def __init__(self):
        self.pattern_registry = PatternRegistry()
        self.entropy_detector = EntropyDetector()
        self.enable_entropy_detection = True
        self.custom_redactors = []
        self.stats = RedactionStats()
        self.trace_enabled = False
        self.traces: List[RedactionTrace] = []
    
    def configure(self, config: Dict[str, Any]):
        """Configure the redaction engine."""
        if 'entropy_threshold' in config:
            self.entropy_detector.threshold = config['entropy_threshold']
        
        if 'entropy_min_length' in config:
            self.entropy_detector.min_length = config['entropy_min_length']
        
        if 'enable_entropy_detection' in config:
            self.enable_entropy_detection = config['enable_entropy_detection']
        
        if 'trace_enabled' in config:
            self.trace_enabled = config['trace_enabled']
    
    def add_custom_redactor(self, redactor_func):
        """Add a custom redaction function."""
        self.custom_redactors.append(redactor_func)
    
    def redact_line(self, 
                   line: str, 
                   line_number: Optional[int] = None,
                   file_path: Optional[str] = None) -> Tuple[str, List[RedactionTrace]]:
        """
        Redact sensitive information from a single line.
        
        Args:
            line: Input line to redact
            line_number: Optional line number for tracing
            file_path: Optional file path for tracing
            
        Returns:
            Tuple of (redacted_line, list_of_traces)
        """
        redacted_line = line
        line_traces = []
        
        # Pattern-based redaction
        for pattern_name, pattern in self.pattern_registry.patterns.items():
            matches = list(pattern.finditer(redacted_line))
            
            for match in matches:
                original_value = match.group()
                redacted_value = f"[REDACTED_{pattern_name.upper()}]"
                
                redacted_line = redacted_line.replace(original_value, redacted_value, 1)
                
                # Update stats
                self.stats.redactions_by_pattern[pattern_name] = \
                    self.stats.redactions_by_pattern.get(pattern_name, 0) + 1
                self.stats.total_redactions += 1
                
                # Create trace if enabled
                if self.trace_enabled:
                    trace = RedactionTrace(
                        original_value=original_value,
                        redacted_value=redacted_value,
                        reason=RedactionReason.PATTERN_MATCH,
                        pattern_name=pattern_name,
                        line_number=line_number,
                        file_path=file_path
                    )
                    line_traces.append(trace)
        
        # Entropy-based detection
        if self.enable_entropy_detection:
            secrets = self.entropy_detector.detect_secrets_in_line(redacted_line)
            
            for secret_token, entropy_score in secrets:
                # Avoid double-redaction of already redacted content
                if "[REDACTED_" not in secret_token:
                    redacted_value = "[REDACTED_SECRET]"
                    redacted_line = redacted_line.replace(secret_token, redacted_value, 1)
                    
                    self.stats.entropy_detections += 1
                    self.stats.total_redactions += 1
                    
                    if self.trace_enabled:
                        trace = RedactionTrace(
                            original_value=secret_token,
                            redacted_value=redacted_value,
                            reason=RedactionReason.ENTROPY_DETECTION,
                            pattern_name=None,
                            line_number=line_number,
                            file_path=file_path,
                            entropy_score=entropy_score
                        )
                        line_traces.append(trace)
        
        # Custom redactors
        from sanilog.utils.logging import logger
        for redactor_func in self.custom_redactors:
            try:
                redacted_line = redactor_func(redacted_line)
            except Exception as e:
                # Log error but don't fail the redaction
                logger.error(f"Custom redactor error: {e}")
        
        self.stats.total_lines_processed += 1
        
        if self.trace_enabled:
            self.traces.extend(line_traces)
        
        return redacted_line, line_traces
    
    def redact_text(self, text: str, file_path: Optional[str] = None) -> Tuple[str, List[RedactionTrace]]:
        """Redact multiple lines of text."""
        lines = text.split('\n')
        redacted_lines = []
        all_traces = []
        
        for line_number, line in enumerate(lines, 1):
            redacted_line, line_traces = self.redact_line(line, line_number, file_path)
            redacted_lines.append(redacted_line)
            all_traces.extend(line_traces)
        
        return '\n'.join(redacted_lines), all_traces
    
    def get_stats(self) -> RedactionStats:
        """Get redaction statistics."""
        return self.stats
    
    def get_traces(self) -> List[RedactionTrace]:
        """Get all redaction traces."""
        return self.traces
    
    def reset_stats(self):
        """Reset statistics."""
        self.stats = RedactionStats()
        self.traces = []
    
    def export_traces_json(self, file_path: Union[str, Path]):
        """Export traces to JSON file."""
        traces_data = [asdict(trace) for trace in self.traces]
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(traces_data, f, indent=2, default=str)


# Convenience function for simple redaction
