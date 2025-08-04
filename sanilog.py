#!/usr/bin/env python3
"""
Sanilog: Log Sanitizer and Anonymizer

A professional CLI tool to sanitize log files by detecting and replacing 
sensitive data for safe sharing in bug reports and documentation.

Author: VK0101011001001011
License: MIT
"""

import re
import argparse
import sys
import logging
from pathlib import Path
from typing import Dict, Optional, TextIO
from dataclasses import dataclass
from collections import OrderedDict


@dataclass
class SanitizationStats:
    """Track sanitization statistics."""
    lines_processed: int = 0
    total_replacements: int = 0
    replacements_by_type: Dict[str, int] = None
    
    def __post_init__(self):
        if self.replacements_by_type is None:
            self.replacements_by_type = {}


class LogSanitizer:
    """Professional log sanitizer with comprehensive pattern matching."""
    
    # Comprehensive regex patterns for sensitive data detection
    # Order matters - more specific patterns should come first
    SENSITIVE_PATTERNS = OrderedDict([
        # JWT tokens (must come before general API keys)
        ('jwt_token', {
            'pattern': r'\beyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\b',
            'replacement': '[REDACTED_JWT]'
        }),
        
        # Bearer tokens (must come before general API keys)  
        ('bearer_token', {
            'pattern': r'\bBearer\s+[a-zA-Z0-9._-]+\b',
            'replacement': 'Bearer [REDACTED_TOKEN]'
        }),
        
        # Cryptographic hashes (must come before general API keys)
        ('sha256', {
            'pattern': r'\b[a-fA-F0-9]{64}\b',
            'replacement': '[REDACTED_SHA256]'
        }),
        ('sha1', {
            'pattern': r'\b[a-fA-F0-9]{40}\b',
            'replacement': '[REDACTED_SHA1]'
        }),
        ('md5', {
            'pattern': r'\b[a-fA-F0-9]{32}\b',
            'replacement': '[REDACTED_MD5]'
        }),
        
        # UUIDs (must come before general API keys)
        ('uuid', {
            'pattern': r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b',
            'replacement': '[REDACTED_UUID]'
        }),
        
        # Network addresses
        ('ipv4', {
            'pattern': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
            'replacement': '[REDACTED_IP]'
        }),
        ('ipv6', {
            'pattern': r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b|(?=.*::)(?!.*::.+::)(?:[0-9a-fA-F]{1,4}:)*::(?:[0-9a-fA-F]{1,4}:)*[0-9a-fA-F]{1,4}\b',
            'replacement': '[REDACTED_IPV6]'
        }),
        ('mac_address', {
            'pattern': r'\b(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}\b',
            'replacement': '[REDACTED_MAC]'
        }),
        
        # Email and communication
        ('email', {
            'pattern': r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
            'replacement': '[REDACTED_EMAIL]'
        }),
        
        # Credit card numbers (basic pattern)
        ('credit_card', {
            'pattern': r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b',
            'replacement': '[REDACTED_CARD]'
        }),
        
        # Social Security Numbers (US format)
        ('ssn', {
            'pattern': r'\b\d{3}-\d{2}-\d{4}\b',
            'replacement': '[REDACTED_SSN]'
        }),
        
        # Phone numbers (various formats)
        ('phone', {
            'pattern': r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
            'replacement': '[REDACTED_PHONE]'
        }),
        
        # API keys (broad pattern, comes last to avoid false positives)
        ('api_key', {
            'pattern': r'\b[a-zA-Z0-9]{32,64}\b',
            'replacement': '[REDACTED_API_KEY]'
        })
    ])
    
    def __init__(self, custom_patterns: Optional[Dict] = None, verbose: bool = False):
        """
        Initialize the sanitizer.
        
        Args:
            custom_patterns: Additional patterns to include
            verbose: Enable verbose logging
        """
        self.patterns = self.SENSITIVE_PATTERNS.copy()
        if custom_patterns:
            self.patterns.update(custom_patterns)
        
        self.verbose = verbose
        self.stats = SanitizationStats()
        
        # Compile regex patterns for better performance
        self.compiled_patterns = {}
        for name, config in self.patterns.items():
            try:
                self.compiled_patterns[name] = {
                    'regex': re.compile(config['pattern']),
                    'replacement': config['replacement']
                }
            except re.error as e:
                logging.warning(f"Invalid regex pattern for {name}: {e}")
    
    def clean_line(self, line: str) -> str:
        """
        Sanitize a single line by replacing sensitive data.
        
        Args:
            line: Input line to sanitize
            
        Returns:
            Sanitized line with sensitive data replaced
        """
        cleaned_line = line
        line_replacements = 0
        
        for pattern_name, config in self.compiled_patterns.items():
            matches = list(config['regex'].finditer(cleaned_line))
            if matches:
                replacement_count = len(matches)
                cleaned_line = config['regex'].sub(config['replacement'], cleaned_line)
                
                # Update statistics
                line_replacements += replacement_count
                self.stats.replacements_by_type[pattern_name] = (
                    self.stats.replacements_by_type.get(pattern_name, 0) + replacement_count
                )
                
                if self.verbose:
                    logging.info(f"Replaced {replacement_count} {pattern_name} pattern(s)")
        
        self.stats.total_replacements += line_replacements
        return cleaned_line
    
    def process_file(self, input_path: str, output_path: Optional[str] = None, 
                    inplace: bool = False, encoding: str = 'utf-8') -> SanitizationStats:
        """
        Process a log file and sanitize sensitive data.
        
        Args:
            input_path: Path to input file
            output_path: Path to output file (optional)
            inplace: Overwrite input file
            encoding: File encoding
            
        Returns:
            Sanitization statistics
        """
        input_file = Path(input_path)
        
        if not input_file.exists():
            raise FileNotFoundError(f"Input file '{input_path}' does not exist")
        
        if not input_file.is_file():
            raise ValueError(f"'{input_path}' is not a regular file")
        
        # Reset statistics for new file
        self.stats = SanitizationStats()
        
        # Determine output strategy
        if inplace:
            temp_file = input_file.with_suffix(input_file.suffix + '.tmp')
            output_handle = open(temp_file, 'w', encoding=encoding)
        elif output_path:
            output_handle = open(output_path, 'w', encoding=encoding)
        else:
            output_handle = sys.stdout
        
        try:
            with open(input_file, 'r', encoding=encoding) as infile:
                for line_num, line in enumerate(infile, 1):
                    cleaned_line = self.clean_line(line)
                    output_handle.write(cleaned_line)
                    self.stats.lines_processed += 1
                    
                    if self.verbose and line_num % 1000 == 0:
                        logging.info(f"Processed {line_num} lines...")
            
            # Handle inplace replacement
            if inplace:
                output_handle.close()
                temp_file.replace(input_file)
                logging.info(f"File '{input_path}' updated in place")
            elif output_path:
                output_handle.close()
                logging.info(f"Sanitized output written to '{output_path}'")
            
        except UnicodeDecodeError as e:
            raise ValueError(f"Unable to decode file '{input_path}' with encoding '{encoding}': {e}")
        except Exception as e:
            # Clean up temp file if inplace operation fails
            if inplace and 'temp_file' in locals():
                temp_file.unlink(missing_ok=True)
            raise RuntimeError(f"Error processing file: {e}")
        finally:
            if output_handle != sys.stdout:
                output_handle.close()
        
        return self.stats
    
    def print_stats(self):
        """Print sanitization statistics."""
        print(f"\nSanitization Summary:")
        print(f"Lines processed: {self.stats.lines_processed}")
        print(f"Total replacements: {self.stats.total_replacements}")
        
        if self.stats.replacements_by_type:
            print("\nReplacements by type:")
            for pattern_type, count in sorted(self.stats.replacements_by_type.items()):
                print(f"  {pattern_type}: {count}")


def setup_logging(verbose: bool = False):
    """Configure logging based on verbosity level."""
    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Sanitize log files by replacing sensitive data with placeholders',
        prog='sanilog',
        epilog='For bug reports and documentation: https://github.com/VK0101011001001011/sanilog'
    )
    
    parser.add_argument(
        'input',
        help='Path to the input log file to sanitize'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Path to the output sanitized log file (default: stdout)'
    )
    
    parser.add_argument(
        '--inplace',
        action='store_true',
        help='Overwrite the input file with sanitized content'
    )
    
    parser.add_argument(
        '--encoding',
        default='utf-8',
        help='File encoding (default: utf-8)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show sanitization statistics'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Validate arguments
    if args.inplace and args.output:
        parser.error("Cannot use --inplace and --output together")
    
    try:
        # Initialize sanitizer
        sanitizer = LogSanitizer(verbose=args.verbose)
        
        # Process file
        if args.verbose:
            logging.info(f"Starting sanitization of '{args.input}'")
        
        stats = sanitizer.process_file(
            args.input, 
            args.output, 
            args.inplace,
            args.encoding
        )
        
        # Show statistics if requested
        if args.stats or args.verbose:
            sanitizer.print_stats()
        
        if args.verbose:
            logging.info("Sanitization completed successfully")
            
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        logging.error(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logging.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
