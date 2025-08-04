"""
LogVeil Structured Data Processor
Handles redaction of structured data formats (JSON, YAML, XML) with key-path-based rules.
"""

import json
import yaml
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Union, Optional, Tuple
from pathlib import Path
import re
from dataclasses import dataclass

from core.redactor import RedactionEngine, RedactionTrace, RedactionReason


@dataclass
class KeyPathMatch:
    """Represents a matched key path for redaction."""
    path: str
    value: Any
    action: str  # redact, remove, mask
    replacement: Optional[str] = None


class StructuredDataProcessor:
    """Processes structured data formats with key-path-based redaction rules."""
    
    def __init__(self, redaction_engine: RedactionEngine):
        self.redaction_engine = redaction_engine
        self.key_path_rules = []
    
    def add_key_path_rule(self, path_pattern: str, action: str = "redact", replacement: Optional[str] = None):
        """Add a key path rule for structured data redaction."""
        self.key_path_rules.append({
            'pattern': path_pattern,
            'action': action,
            'replacement': replacement,
            'compiled': self._compile_path_pattern(path_pattern)
        })
    
    def _compile_path_pattern(self, pattern: str) -> re.Pattern:
        """Compile a key path pattern into a regex."""
        # Convert path patterns like "user.*.email" to regex
        # Escape dots and replace * with [^.]+
        regex_pattern = pattern.replace('.', r'\.').replace('*', r'[^.]+')
        return re.compile(f"^{regex_pattern}$")
    
    def process_json(self, data: Union[str, Dict, List], file_path: Optional[str] = None) -> Tuple[Union[Dict, List], List[RedactionTrace]]:
        """Process JSON data for redaction."""
        if isinstance(data, str):
            try:
                parsed_data = json.loads(data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON: {e}")
        else:
            parsed_data = data
        
        traces = []
        redacted_data = self._process_structure(parsed_data, "", traces, file_path)
        
        return redacted_data, traces
    
    def process_yaml(self, data: Union[str, Dict], file_path: Optional[str] = None) -> Tuple[Dict, List[RedactionTrace]]:
        """Process YAML data for redaction."""
        if isinstance(data, str):
            try:
                parsed_data = yaml.safe_load(data)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML: {e}")
        else:
            parsed_data = data
        
        traces = []
        redacted_data = self._process_structure(parsed_data, "", traces, file_path)
        
        return redacted_data, traces
    
    def process_xml(self, xml_string: str, file_path: Optional[str] = None) -> Tuple[str, List[RedactionTrace]]:
        """Process XML data for redaction."""
        try:
            root = ET.fromstring(xml_string)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML: {e}")
        
        traces = []
        self._process_xml_element(root, "", traces, file_path)
        
        return ET.tostring(root, encoding='unicode'), traces
    
    def _process_structure(self, obj: Any, current_path: str, traces: List[RedactionTrace], file_path: Optional[str]) -> Any:
        """Recursively process a data structure."""
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                new_path = f"{current_path}.{key}" if current_path else key
                
                # Check if this path matches any key path rules
                matching_rule = self._find_matching_rule(new_path)
                
                if matching_rule:
                    if matching_rule['action'] == 'remove':
                        # Skip this key entirely
                        traces.append(RedactionTrace(
                            original_value=str(value),
                            redacted_value="[REMOVED]",
                            reason=RedactionReason.CUSTOM_RULE,
                            pattern_name=matching_rule['pattern'],
                            line_number=None,
                            file_path=file_path
                        ))
                        continue
                    elif matching_rule['action'] == 'redact':
                        replacement = matching_rule['replacement'] or f"[REDACTED_{key.upper()}]"
                        result[key] = replacement
                        traces.append(RedactionTrace(
                            original_value=str(value),
                            redacted_value=replacement,
                            reason=RedactionReason.CUSTOM_RULE,
                            pattern_name=matching_rule['pattern'],
                            line_number=None,
                            file_path=file_path
                        ))
                        continue
                    elif matching_rule['action'] == 'mask':
                        masked_value = self._mask_value(value)
                        result[key] = masked_value
                        traces.append(RedactionTrace(
                            original_value=str(value),
                            redacted_value=str(masked_value),
                            reason=RedactionReason.CUSTOM_RULE,
                            pattern_name=matching_rule['pattern'],
                            line_number=None,
                            file_path=file_path
                        ))
                        continue
                
                # If no key path rule matches, apply standard redaction to string values
                if isinstance(value, str):
                    redacted_value, line_traces = self.redaction_engine.redact_line(value, file_path=file_path)
                    result[key] = redacted_value
                    
                    # Update trace paths
                    for trace in line_traces:
                        trace.file_path = f"{file_path}:{new_path}" if file_path else new_path
                    traces.extend(line_traces)
                else:
                    # Recursively process nested structures
                    result[key] = self._process_structure(value, new_path, traces, file_path)
            
            return result
        
        elif isinstance(obj, list):
            result = []
            for i, item in enumerate(obj):
                new_path = f"{current_path}[{i}]"
                result.append(self._process_structure(item, new_path, traces, file_path))
            return result
        
        elif isinstance(obj, str):
            # Apply standard redaction to string values
            redacted_value, line_traces = self.redaction_engine.redact_line(obj, file_path=file_path)
            
            # Update trace paths
            for trace in line_traces:
                trace.file_path = f"{file_path}:{current_path}" if file_path else current_path
            traces.extend(line_traces)
            
            return redacted_value
        
        else:
            # Return primitive values (numbers, booleans, None) unchanged
            return obj
    
    def _process_xml_element(self, element: ET.Element, current_path: str, traces: List[RedactionTrace], file_path: Optional[str]):
        """Process XML element for redaction."""
        element_path = f"{current_path}.{element.tag}" if current_path else element.tag
        
        # Process text content
        if element.text and element.text.strip():
            matching_rule = self._find_matching_rule(element_path)
            
            if matching_rule:
                if matching_rule['action'] == 'remove':
                    element.text = ""
                elif matching_rule['action'] == 'redact':
                    replacement = matching_rule['replacement'] or f"[REDACTED_{element.tag.upper()}]"
                    traces.append(RedactionTrace(
                        original_value=element.text,
                        redacted_value=replacement,
                        reason=RedactionReason.CUSTOM_RULE,
                        pattern_name=matching_rule['pattern'],
                        line_number=None,
                        file_path=f"{file_path}:{element_path}" if file_path else element_path
                    ))
                    element.text = replacement
                elif matching_rule['action'] == 'mask':
                    masked_value = self._mask_value(element.text)
                    element.text = str(masked_value)
            else:
                # Apply standard redaction
                redacted_text, line_traces = self.redaction_engine.redact_line(element.text, file_path=file_path)
                element.text = redacted_text
                
                for trace in line_traces:
                    trace.file_path = f"{file_path}:{element_path}" if file_path else element_path
                traces.extend(line_traces)
        
        # Process attributes
        for attr_name, attr_value in element.attrib.items():
            attr_path = f"{element_path}@{attr_name}"
            matching_rule = self._find_matching_rule(attr_path)
            
            if matching_rule:
                if matching_rule['action'] == 'remove':
                    del element.attrib[attr_name]
                elif matching_rule['action'] == 'redact':
                    replacement = matching_rule['replacement'] or f"[REDACTED_{attr_name.upper()}]"
                    element.attrib[attr_name] = replacement
                elif matching_rule['action'] == 'mask':
                    element.attrib[attr_name] = str(self._mask_value(attr_value))
            else:
                # Apply standard redaction
                redacted_attr, line_traces = self.redaction_engine.redact_line(attr_value, file_path=file_path)
                element.attrib[attr_name] = redacted_attr
                
                for trace in line_traces:
                    trace.file_path = f"{file_path}:{attr_path}" if file_path else attr_path
                traces.extend(line_traces)
        
        # Process child elements recursively
        for child in element:
            self._process_xml_element(child, element_path, traces, file_path)
    
    def _find_matching_rule(self, path: str) -> Optional[Dict]:
        """Find the first matching key path rule for a given path."""
        for rule in self.key_path_rules:
            if rule['compiled'].match(path):
                return rule
        return None
    
    def _mask_value(self, value: Any) -> str:
        """Mask a value by showing only first and last characters."""
        str_value = str(value)
        if len(str_value) <= 2:
            return "*" * len(str_value)
        elif len(str_value) <= 4:
            return str_value[0] + "*" * (len(str_value) - 2) + str_value[-1]
        else:
            return str_value[:2] + "*" * (len(str_value) - 4) + str_value[-2:]
    
    def export_redacted_json(self, data: Dict, output_path: Union[str, Path], indent: int = 2):
        """Export redacted data as JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    
    def export_redacted_yaml(self, data: Dict, output_path: Union[str, Path]):
        """Export redacted data as YAML."""
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


def process_structured_file(file_path: Union[str, Path], 
                           redaction_engine: RedactionEngine,
                           key_path_rules: Optional[List[Dict]] = None,
                           output_path: Optional[Union[str, Path]] = None) -> Tuple[Any, List[RedactionTrace]]:
    """
    Process a structured data file for redaction.
    
    Args:
        file_path: Path to the input file
        redaction_engine: Configured redaction engine
        key_path_rules: List of key path rules to apply
        output_path: Optional output path for redacted file
        
    Returns:
        Tuple of (redacted_data, traces)
    """
    file_path = Path(file_path)
    processor = StructuredDataProcessor(redaction_engine)
    
    # Add key path rules if provided
    if key_path_rules:
        for rule in key_path_rules:
            processor.add_key_path_rule(
                rule.get('path', ''),
                rule.get('action', 'redact'),
                rule.get('replacement')
            )
    
    # Read and process file based on extension
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if file_path.suffix.lower() == '.json':
        redacted_data, traces = processor.process_json(content, str(file_path))
        
        if output_path:
            processor.export_redacted_json(redacted_data, output_path)
    
    elif file_path.suffix.lower() in ['.yaml', '.yml']:
        redacted_data, traces = processor.process_yaml(content, str(file_path))
        
        if output_path:
            processor.export_redacted_yaml(redacted_data, output_path)
    
    elif file_path.suffix.lower() == '.xml':
        redacted_data, traces = processor.process_xml(content, str(file_path))
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(redacted_data)
    
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    return redacted_data, traces


if __name__ == "__main__":
    # Test the structured data processor
    from core.redactor import RedactionEngine
    
    # Sample JSON data
    test_data = {
        "user": {
            "id": 12345,
            "email": "user@example.com",
            "password": "secret123",
            "profile": {
                "name": "John Doe",
                "phone": "555-123-4567"
            }
        },
        "session": {
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature",
            "ip_address": "192.168.1.100"
        },
        "logs": [
            "User login from 10.0.0.1",
            "API key: sk-1234567890abcdef"
        ]
    }
    
    # Create processor
    engine = RedactionEngine()
    processor = StructuredDataProcessor(engine)
    
    # Add key path rules
    processor.add_key_path_rule("user.email", "redact")
    processor.add_key_path_rule("user.password", "remove")
    processor.add_key_path_rule("session.token", "redact")
    processor.add_key_path_rule("user.profile.phone", "mask")
    
    # Process data
    redacted_data, traces = processor.process_json(test_data)
    
    print("Original data:")
    print(json.dumps(test_data, indent=2))
    print("\nRedacted data:")
    print(json.dumps(redacted_data, indent=2))
    print(f"\nRedaction traces: {len(traces)}")
    for trace in traces:
        print(f"  {trace.reason.value}: {trace.original_value} -> {trace.redacted_value}")
