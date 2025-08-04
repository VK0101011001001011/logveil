from typing import List, Dict
from dataclasses import dataclass

@dataclass
class TraceItem:
    original: str
    redacted: str
    pattern: str
    line: str
    file: str

@dataclass
class RedactionResult:
    sanitized_line: str
    match_counts: Dict[str, int]

@dataclass
class Config:
    enable_entropy_detection: bool
    entropy_threshold: float
    redaction_rules: List[Dict]

__all__ = ['TraceItem', 'RedactionResult', 'Config']
