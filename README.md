# LogVeil

## Production-grade log sanitization and redaction engine

LogVeil is a comprehensive, language-agnostic log sanitization toolkit designed for modern DevOps and security teams. It provides intelligent detection and redaction of sensitive data in log files, supporting multiple processing engines and deployment modes.

---

## Mission Statement

LogVeil serves as the definitive solution for log sanitization in production environments. By combining intelligent pattern detection, entropy analysis, and customizable redaction policies, LogVeil enables teams to safely share logs for debugging and analysis while maintaining strict data privacy and compliance requirements.

---

## Quick Start

### Installation

```bash
# Install from PyPI (recommended)
pip install logveil

# Or install from source
git clone https://github.com/logveil/logveil.git
cd logveil
pip install -e .
```

### Basic Usage

```bash
# Sanitize a log file
logveil sanitize app.log

# Use specific profile  
logveil sanitize app.log --profile nginx

# Output to file
logveil sanitize app.log --output clean.log

# Enable entropy detection
logveil sanitize app.log --detect-entropy --entropy-threshold 4.5
```

### API Usage

```python
from logveil import RedactionEngine, ProfileManager

# Initialize engine
engine = RedactionEngine()
profiles = ProfileManager()

# Load profile
profile = profiles.get_profile("application")
engine.load_profile(profile)

# Sanitize text
result = engine.redact_line("User admin@company.com logged in from 192.168.1.100")
print(result.sanitized_text)  # User [REDACTED_EMAIL] logged in from [REDACTED_IP]
```

---

## Architecture

LogVeil employs a modular, multi-engine architecture optimized for different use cases:

```text
┌─────────────────────────────────────────────────────────────┐
│                        LogVeil CLI                          │
├─────────────────────────────────────────────────────────────┤
│  Engine Dispatcher  │  Profile Manager  │  Configuration    │
├─────────────────────────────────────────────────────────────┤
│           Redaction Engine (Python Core)                    │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │   Pattern       │ │   Entropy       │ │   Structured    ││
│  │   Matching      │ │   Detection     │ │   Data Parser   ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
├─────────────────────────────────────────────────────────────┤
│            Performance Engines (Optional)                   │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │   Rust Engine   │ │   Go Bridge     │ │   Native FFI    ││
│  │   (High Speed)  │ │   (Concurrent)  │ │   (C Library)   ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
├─────────────────────────────────────────────────────────────┤
│                    Output Processors                        │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │   File Writer   │ │   API Server    │ │   Stream        ││
│  │                 │ │   (REST/JSON)   │ │   Processor     ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Engine Types

| Engine | Use Case | Performance | Features |
|--------|----------|-------------|----------|
| **Python** | Development, Debugging | Good | Full feature set, extensible |
| **Rust** | Production, High-throughput | Excellent | Optimized patterns, minimal overhead |
| **Hybrid** | Balanced workloads | Very Good | Python flexibility + Rust speed |
| **Go Bridge** | Concurrent processing | Very Good | Parallel file processing |

---

## Supported Patterns

LogVeil includes comprehensive pattern detection for sensitive data:

| Type | Pattern Example | Replacement | Configurable |
|------|-----------------|-------------|--------------|
| **Network** | | | |
| IPv4 Address | `192.168.1.100` | `[REDACTED_IP]` | ✓ |
| IPv6 Address | `2001:db8::1` | `[REDACTED_IPV6]` | ✓ |
| MAC Address | `00:1B:44:11:3A:B7` | `[REDACTED_MAC]` | ✓ |
| **Authentication** | | | |
| Email Address | `user@domain.com` | `[REDACTED_EMAIL]` | ✓ |
| JWT Token | `eyJhbGciOiJIUzI1Ni...` | `[REDACTED_JWT]` | ✓ |
| Bearer Token | `Bearer abc123...` | `Bearer [REDACTED_TOKEN]` | ✓ |
| API Key | `sk-1234567890abcdef` | `[REDACTED_API_KEY]` | ✓ |
| **Cryptographic** | | | |
| SHA256 Hash | `a665a45920422f9d...` | `[REDACTED_SHA256]` | ✓ |
| SHA1 Hash | `aaf4c61ddcc5e8a2...` | `[REDACTED_SHA1]` | ✓ |
| MD5 Hash | `5d41402abc4b2a76...` | `[REDACTED_MD5]` | ✓ |
| **Identifiers** | | | |
| UUID | `123e4567-e89b-12d3...` | `[REDACTED_UUID]` | ✓ |
| Credit Card | `4111-1111-1111-1111` | `[REDACTED_CARD]` | ✓ |
| SSN (US) | `123-45-6789` | `[REDACTED_SSN]` | ✓ |
| Phone Number | `(555) 123-4567` | `[REDACTED_PHONE]` | ✓ |
| **High Entropy** | | | |
| Secrets | `gAAAAABhZ2ljc...` | `[REDACTED_SECRET]` | ✓ |
| Private Keys | `-----BEGIN PRIVATE...` | `[REDACTED_PRIVATE_KEY]` | ✓ |

---

## CLI Reference

### Core Commands

```bash
# Sanitize files
logveil sanitize <input> [options]
logveil batch <directory> [options]

# Profile management  
logveil profiles list
logveil profiles create <name>
logveil profiles validate <name>

# Engine management
logveil engines list
logveil engines benchmark
logveil engines test

# Server mode
logveil serve [options]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--profile <name>` | Use predefined profile | `application` |
| `--output <file>` | Output file path | stdout |
| `--engine <type>` | Processing engine | `auto` |
| `--entropy-threshold <float>` | Entropy detection threshold | 4.5 |
| `--trace <file>` | Save redaction trace | disabled |
| `--format <type>` | Output format (text/json) | `text` |
| `--quiet` | Suppress progress output | false |
| `--no-color` | Disable colored output | false |

### Examples

```bash
# Basic sanitization
logveil sanitize /var/log/app.log

# Use custom profile with trace
logveil sanitize app.log --profile nginx --trace redactions.json

# High-performance batch processing
logveil batch /logs --engine rust --output-dir /clean-logs

# Enable entropy detection for unknown secrets
logveil sanitize app.log --detect-entropy --entropy-threshold 4.0

# API mode with custom configuration
logveil serve --host 0.0.0.0 --port 8080 --workers 4
```

---

## API Server

LogVeil includes a production-ready REST API server for integration into existing systems.

### Starting the Server

```bash
logveil serve --host 0.0.0.0 --port 8080
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/sanitize/text` | Sanitize raw text |
| `POST` | `/sanitize/file` | Upload and sanitize file |
| `POST` | `/batch/sanitize` | Batch processing |
| `GET` | `/profiles` | List available profiles |
| `GET` | `/engines` | List available engines |
| `GET` | `/health` | Health check |
| `GET` | `/metrics` | Performance metrics |

### Example Requests

```bash
# Sanitize text
curl -X POST "http://localhost:8080/sanitize/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "User admin@company.com from 192.168.1.1",
    "profile": "application",
    "engine": "rust"
  }'

# Upload file
curl -X POST "http://localhost:8080/sanitize/file" \
  -F "file=@app.log" \
  -F "profile=nginx" \
  -F "trace=true"

# Batch processing
curl -X POST "http://localhost:8080/batch/sanitize" \
  -H "Content-Type: application/json" \
  -d '{
    "files": ["log1.txt", "log2.txt"],
    "profile": "application",
    "output_format": "json"
  }'
```

---

## Profiles

LogVeil uses JSON-based profiles to define redaction policies for different log types.

### Built-in Profiles

| Profile | Use Case | Patterns | Entropy |
|---------|----------|----------|---------|
| `application` | Generic application logs | All common patterns | Enabled |
| `nginx` | Nginx access/error logs | IPs, UAs, auth tokens | Disabled |
| `docker` | Container logs | Container IDs, image names | Enabled |
| `cloudtrail` | AWS CloudTrail logs | ARNs, account IDs, principals | Enabled |

### Creating Custom Profiles

```json
{
  "name": "custom-app",
  "description": "Custom application profile",
  "patterns": [
    {
      "name": "customer_id",
      "pattern": "customer_id=\\d+",
      "replacement": "customer_id=[REDACTED]",
      "enabled": true
    }
  ],
  "entropy_config": {
    "enabled": true,
    "threshold": 4.5,
    "min_length": 8
  }
}
```

---

## Performance

LogVeil is optimized for production workloads with multiple engine options:

### Benchmarks

Tested on Intel i7-10700K, 32GB RAM, processing 1GB log file (10M lines)

| Engine | Throughput | Memory Usage | CPU Usage |
|--------|------------|--------------|-----------|
| Python | 50 MB/s | 200 MB | 60% (1 core) |
| Rust | 180 MB/s | 50 MB | 40% (1 core) |
| Go Bridge | 120 MB/s | 80 MB | 80% (4 cores) |
| Hybrid | 150 MB/s | 120 MB | 70% (2 cores) |

### Optimization Tips

1. **Use Rust engine** for maximum throughput
2. **Enable batch mode** for multiple files
3. **Disable entropy detection** if not needed
4. **Use specific profiles** to reduce pattern count
5. **Stream processing** for large files

---

## Integration Examples

### GitHub Actions

```yaml
name: Log Sanitization
on: [push]
jobs:
  sanitize:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup LogVeil
        run: pip install logveil
      - name: Sanitize logs
        run: |
          logveil batch logs/ --output-dir sanitized/
          logveil profiles validate custom-profile.json
```

### Docker

```dockerfile
FROM python:3.11-slim
RUN pip install logveil
COPY profiles/ /app/profiles/
WORKDIR /app
CMD ["logveil", "serve", "--host", "0.0.0.0"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: logveil-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: logveil-api
  template:
    metadata:
      labels:
        app: logveil-api
    spec:
      containers:
      - name: logveil
        image: logveil/logveil:2.0.0
        ports:
        - containerPort: 8080
        env:
        - name: LOGVEIL_ENGINE
          value: "rust"
```

---

## Development

### Setup

```bash
git clone https://github.com/logveil/logveil.git
cd logveil
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .[dev]
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=logveil --cov-report=html

# Run performance benchmarks
python tools/testbench/benchmark.py

# Test specific engine
pytest tests/test_rust_engine.py
```

### Building Rust Components

```bash
cd core/
cargo build --release
python setup.py build_ext --inplace
```

---

## Security

LogVeil follows security best practices:

- **No data retention**: Processed data is never stored
- **Memory safety**: Rust components prevent buffer overflows
- **Input validation**: All inputs are validated and sanitized
- **Audit logging**: Optional trace logs for compliance
- **Configurable policies**: Fine-grained control over redaction

### Reporting Security Issues

Please report security vulnerabilities to [security@logveil.dev](mailto:security@logveil.dev). Do not use public issue trackers for security-related concerns.

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Links

- [Issue Tracker](https://github.com/logveil/logveil/issues)
- [Discussions](https://github.com/logveil/logveil/discussions)
- [Documentation](https://docs.logveil.dev)
- [Changelog](CHANGELOG.md)

---

**LogVeil** - *Secure logs, simplified*
