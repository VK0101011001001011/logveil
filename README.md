# Sanilog - Log Sanitizer & Anonymizer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)

A professional CLI tool to sanitize log files by detecting and replacing sensitive data for safe sharing in bug reports, documentation, and public forums.

## Features

Sanilog is a powerful log sanitization tool designed to identify and redact sensitive information from log files. It supports:

🔒 **Comprehensive Detection**
- Detects and redacts sensitive data such as IP addresses, email addresses, cryptographic hashes, and high-entropy secrets.
- Includes support for structured data like JWT tokens, API keys, UUIDs, and credit card numbers.

📊 **Detailed Statistics**
- Provides a summary of redactions, including counts for each type of sensitive data.
- Useful for auditing and understanding the scope of sanitization.

⚡ **High Performance**
- Optimized for large-scale log processing with multi-threaded execution.
- Includes entropy-based detection for forensic-grade sanitization.

🛡️ **Safe Operations**
- Ensures safe handling of files with options for in-place modifications or saving sanitized copies.
- Temporary files are used to prevent data loss during processing.

🗂️ **Multi-File Support**
- Processes entire folders of log files, preserving subfolder structure.
- Automatically skips hidden files and unsupported formats.

📋 **Trace Logging**
- Generates structured JSON logs for every redaction, including original and redacted values.
- Ideal for compliance, audits, and debugging.

## Installation

```bash
# Clone the repository
git clone https://github.com/VK0101011001001011/sanilog.git
cd sanilog

# Make executable (optional)
chmod +x sanilog.py
```

## Usage

Sanilog can be used to sanitize individual log files or entire folders. It supports various advanced options for customization.

### Basic Usage

```bash
# Output sanitized content to stdout
python sanilog.py /path/to/logfile.log

# Save sanitized content to a new file
python sanilog.py /path/to/logfile.log -o /path/to/cleaned.log

# Overwrite the original file with sanitized content
python sanilog.py /path/to/logfile.log --inplace

# Show sanitization statistics
python sanilog.py /path/to/logfile.log --stats
```

### Advanced Options

```bash
# Enable verbose mode with statistics
python sanilog.py /path/to/logfile.log -v --stats

# Specify file encoding
python sanilog.py /path/to/logfile.log --encoding iso-8859-1

# Detect high-entropy secrets
python sanilog.py /path/to/logfile.log --detect-entropy

# Process entire folders of log files
python sanilog.py --input /path/to/logs --output-dir /path/to/sanitized_logs

# Save trace logs for auditing
python sanilog.py /path/to/logfile.log --trace-output trace.json

# Display help information
python sanilog.py --help
```

## Examples

### Before Sanitization
```
User john.doe@company.com logged in from 192.168.1.100
API Key: abc123def456ghi789jkl012mno345pqr678
JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
Transaction hash: a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3
Secret key: abcdefghijklmnopqrstuvwxyz1234567890
```

### After Sanitization
```
User [REDACTED_EMAIL] logged in from [REDACTED_IP]
API Key: [REDACTED_API_KEY]
JWT: [REDACTED_JWT]
Transaction hash: [REDACTED_SHA256]
Secret key: [REDACTED_SECRET]
```

## Supported Patterns

Sanilog supports a wide range of patterns for detecting sensitive data:

| Type | Example | Replacement |
|------|---------|-------------|
| IPv4 | `192.168.1.1` | `[REDACTED_IP]` |
| IPv6 | `2001:db8::1` | `[REDACTED_IPV6]` |
| Email | `user@domain.com` | `[REDACTED_EMAIL]` |
| JWT | `eyJ...` | `[REDACTED_JWT]` |
| API Key | `32-64 char alphanumeric` | `[REDACTED_API_KEY]` |
| SHA256 | `64 hex characters` | `[REDACTED_SHA256]` |
| SHA1 | `40 hex characters` | `[REDACTED_SHA1]` |
| MD5 | `32 hex characters` | `[REDACTED_MD5]` |
| MAC Address | `00:11:22:33:44:55` | `[REDACTED_MAC]` |
| UUID | `550e8400-e29b-41d4-a716-446655440000` | `[REDACTED_UUID]` |
| Credit Card | `4111111111111111` | `[REDACTED_CARD]` |
| SSN | `123-45-6789` | `[REDACTED_SSN]` |
| Phone | `(555) 123-4567` | `[REDACTED_PHONE]` |
| Bearer Token | `Bearer abc123...` | `Bearer [REDACTED_TOKEN]` |
| High-Entropy Secret | `abcdefghijklmnopqrstuvwxyz1234567890` | `[REDACTED_SECRET]` |

## Command Line Options

Sanilog provides a variety of command-line options for customization:

```
usage: sanilog [-h] [-o OUTPUT] [--inplace] [--encoding ENCODING] [-v] [--stats] [--version] input

positional arguments:
  input                 Path to the input log file or folder to sanitize

options:
  -h, --help            Show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Path to the output sanitized log file (default: stdout)
  --inplace             Overwrite the input file with sanitized content
  --encoding ENCODING   File encoding (default: utf-8)
  -v, --verbose         Enable verbose output
  --stats               Show sanitization statistics
  --version             Show program's version number and exit
```

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)

## Use Cases

Sanilog is ideal for:

- **Bug Reports**: Share logs safely without exposing sensitive infrastructure details.
- **Documentation**: Create sanitized examples for tutorials and documentation.
- **Support Tickets**: Provide logs to support teams without security concerns.
- **Code Reviews**: Include sanitized logs in pull requests.
- **Training**: Use real log patterns without exposing sensitive data.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Security Note

While Sanilog helps remove many common types of sensitive data, always review sanitized output before sharing. Consider that:

- Custom application-specific sensitive patterns may not be covered.
- Context around redacted data might still be sensitive.
- False positives/negatives can occur with complex log formats.

For highly sensitive environments, consider additional manual review.
