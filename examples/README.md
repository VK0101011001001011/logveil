# LogVeil Examples

This directory contains example files for testing and demonstrating LogVeil functionality.

## Files

- `sample_log.txt` - Sample log file with various types of sensitive data for testing LogVeil's detection and redaction capabilities

## Usage

You can use these files to test LogVeil:

```bash
# Using the CLI
logveil examples/sample_log.txt

# Using the module
python -m logveil.cli.logveil_agent examples/sample_log.txt

# With output file
logveil examples/sample_log.txt -o sanitized_output.log
```
