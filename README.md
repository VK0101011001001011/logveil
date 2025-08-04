# 🔥 LogVeil 2.0 — The Last Log Redactor You'll Ever Need

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub release](https://img.shields.io/github/release/logveil/logveil.svg)](https://github.com/logveil/logveil/releases)
[![Docker Pulls](https://img.shields.io/docker/pulls/logveil/logveil.svg)](https://hub.docker.com/r/logveil/logveil)

**Production-grade, intelligent log sanitization platform with adaptive redaction, full audit trails, and multi-language performance optimization.**

LogVeil 2.0 is a complete rewrite and expansion of the original log sanitization tool. It's designed for modern DevOps workflows, compliance requirements, and enterprise-scale log processing.

## ✨ Features

### 🚀 **Multi-Engine Performance**
- **Rust Engine**: High-speed pattern matching (5M+ lines/sec)
- **Go Engine**: Concurrent file streaming for large datasets
- **Python Engine**: Intelligent fallback with full feature support
- **Auto-Detection**: Automatically selects optimal engine for workload

### 🧠 **Intelligent Redaction**
- **Pattern Matching**: 15+ built-in patterns (emails, IPs, tokens, keys)
- **Entropy Detection**: Shannon entropy analysis for unknown secrets
- **Structured Data**: JSON/YAML/XML key-path redaction rules
- **Custom Profiles**: Pre-built profiles for nginx, Docker, CloudTrail, etc.

### � **Full Audit Trail**
- **Redaction Traces**: JSON audit logs showing what was redacted and why
- **Compliance Ready**: GDPR, SOX, HIPAA documentation support
- **Statistics**: Detailed processing metrics and pattern match counts
- **Forensic Mode**: Reversible redaction for authorized personnel

### 🌐 **Multiple Deployment Modes**
- **CLI Tool**: `logveil myapp.log --profile nginx --trace audit.json`
- **API Server**: `logveil --serve --port 8080` (FastAPI with OpenAPI docs)
- **Desktop GUI**: Drag-and-drop interface (Tauri-based)
- **CI/CD Integration**: GitHub Actions, Docker, and pipeline support

### 🔌 **Extensible Architecture**
- **Custom Patterns**: JSON/YAML rule definitions
- **Plugin System**: Python and WASM runtime support
- **Profile System**: Shareable redaction configurations
- **Multi-Format**: Text, JSON, YAML, XML, CSV support

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install logveil

# With server support
pip install "logveil[server]"

# With all features
pip install "logveil[all]"

# From source
git clone https://github.com/logveil/logveil.git
cd logveil && pip install -e .
```

### Basic Usage

```bash
# Sanitize a single log file
logveil app.log

# Use a specific profile
logveil nginx.access.log --profile nginx

# Process directory recursively
logveil logs/ --recursive --output clean_logs/

# Generate audit trail
logveil app.log --trace audit.json --stats

# Preview changes before applying
logveil app.log --preview

# Start API server
logveil --serve --port 8080
```

### API Usage

```python
from logveil import RedactionEngine

# Basic redaction
engine = RedactionEngine()
clean_text, traces = engine.redact_text("User john@example.com logged in from 192.168.1.100")

# With custom profile
engine.configure({"entropy_threshold": 4.5})
clean_logs, audit_trail = engine.redact_file("app.log")
```

## 📋 Built-in Profiles

| Profile | Description | Best For |
|---------|-------------|----------|
| `nginx` | Web server logs | Nginx, Apache access/error logs |
| `docker` | Container logs | Docker, Kubernetes container output |
| `cloudtrail` | AWS audit logs | CloudTrail, CloudWatch logs |
| `application` | App logs | Rails, Django, Node.js applications |

```bash
# List all available profiles
logveil --list-profiles

# Use specific profile
logveil app.log --profile docker
```

## 🛠️ Advanced Configuration

### Custom Redaction Rules

Create `custom-rules.json`:
```json
{
  "credit_card": "\\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\\b",
  "api_token": "\\b[A-Za-z0-9]{32,}\\b",
  "internal_id": "ID-[0-9]{6,}"
}
```

```bash
logveil app.log --rules custom-rules.json
```

### Structured Data Redaction

For JSON/YAML logs with key-path rules:
```bash
# Redact specific JSON keys
logveil data.json --keys-to-redact user.email,auth.token,session.id

# Custom key-path profile
logveil docker-logs.json --profile docker
```

### Entropy-Based Secret Detection

```bash
# Adjust entropy threshold
logveil app.log --entropy-threshold 4.5

# Disable entropy detection
logveil app.log --disable-entropy
```

## 🌐 API Server Mode

Start the REST API server:
```bash
logveil --serve --host 0.0.0.0 --port 8080
```

### API Endpoints

- `POST /sanitize/text` - Sanitize raw text
- `POST /sanitize/file` - Upload and sanitize file
- `GET /profiles` - List available profiles
- `GET /status` - Server statistics
- `POST /batch/sanitize` - Batch processing

### Example API Usage

```bash
# Sanitize text via API
curl -X POST "http://localhost:8080/sanitize/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "User admin@company.com from 192.168.1.1", "profile": "nginx"}'

# Upload file
curl -X POST "http://localhost:8080/sanitize/file" \
  -F "file=@app.log" \
  -F "profile=application" \
  -F "trace=true"
```

## 📊 Performance Benchmarks

| Engine | Lines/sec | Memory Usage | Best For |
|--------|-----------|--------------|----------|
| Rust | 5,000,000+ | Low | Large files, high-throughput |
| Go | 2,000,000+ | Medium | Concurrent processing |
| Python | 500,000+ | High | Complex logic, flexibility |

Benchmark your system:
```bash
logveil --benchmark
```

## 🔧 Configuration

### Engine Selection

```bash
# Auto-detect optimal engine (default)
logveil app.log --engine auto

# Force specific engine
logveil app.log --engine rust
logveil app.log --engine go
logveil app.log --engine python
```

### Output Formats

```bash
# Text output (default)
logveil app.log --format txt

# JSON output with metadata
logveil app.log --format json

# YAML output
logveil app.log --format yaml
```

## 🐳 Docker Usage

```bash
# Pull official image
docker pull logveil/logveil:latest

# Sanitize local files
docker run -v $(pwd):/data logveil/logveil logveil /data/app.log

# Run API server
docker run -p 8080:8080 logveil/logveil logveil --serve --host 0.0.0.0
```

## 🤖 CI/CD Integration

### GitHub Actions

```yaml
name: Sanitize Logs
on: [push]
jobs:
  sanitize:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: logveil/action@v1
        with:
          files: 'logs/*.log'
          profile: 'application'
          output: 'clean-logs/'
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    stages {
        stage('Sanitize Logs') {
            steps {
                sh 'logveil build.log --profile application --output clean-build.log'
                archiveArtifacts artifacts: 'clean-build.log'
            }
        }
    }
}
```

## � Security & Compliance

### GDPR Compliance
- **Right to be Forgotten**: Complete PII removal
- **Data Minimization**: Configurable redaction levels
- **Audit Trail**: Full processing documentation
- **Reversible Redaction**: For authorized data recovery

### Enterprise Features
- **Role-Based Access**: Different redaction levels by user role
- **Encryption**: Encrypted audit trails and temporary files
- **Integration**: SIEM, log management platform plugins
- **Compliance Reports**: Automated compliance documentation

## 📚 Documentation

- **[Installation Guide](docs/installation.md)** - Detailed setup instructions
- **[API Reference](docs/api.md)** - Complete API documentation
- **[Profile Guide](docs/profiles.md)** - Creating custom profiles
- **[Performance Tuning](docs/performance.md)** - Optimization tips
- **[Security Guide](docs/security.md)** - Security best practices

## 🤝 Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for detailed instructions on development setup, testing, adding profiles, plugin integration, and CI/CD.

### Development Setup

```bash
git clone https://github.com/logveil/logveil.git
cd logveil
pip install -e ".[dev]"
pre-commit install
pytest
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🚀 Roadmap

### v2.1 (Q2 2024)
- [ ] Real-time streaming support
- [ ] Machine learning-based pattern detection
- [ ] Advanced XML/HTML processing
- [ ] Kubernetes operator

### v2.2 (Q3 2024)
- [ ] Browser extension for log viewers
- [ ] Elasticsearch/Logstash integration
- [ ] Advanced reversible redaction
- [ ] Multi-tenant API support

## 💬 Community & Support

- **[Discord](https://discord.gg/logveil)** - Community chat
- **[GitHub Issues](https://github.com/logveil/logveil/issues)** - Bug reports
- **[Discussions](https://github.com/logveil/logveil/discussions)** - Feature requests
- **[Documentation](https://docs.logveil.dev)** - Full documentation

---

**LogVeil 2.0** - Because your logs deserve privacy too. 🔐

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
