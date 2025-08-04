# Contributing to LogVeil

Thank you for your interest in contributing to LogVeil! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Code Standards](#code-standards)
- [Submitting Changes](#submitting-changes)
- [Adding Profiles](#adding-profiles)
- [Performance Testing](#performance-testing)

## Development Setup

### Prerequisites

- Python 3.8+

- Rust 1.70+ (for Rust engine components)

- Go 1.19+ (for Go bridge components)

- Git

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/logveil/logveil.git
cd logveil

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Build Rust components (optional)
cd core && cargo build --release && cd ..

# Run initial tests
pytest
```

### Manual Setup

If the quick setup fails, follow these steps:

```bash
# 1. Install base dependencies
pip install -r requirements.txt

# 2. Install development tools
pip install pytest pytest-cov black isort mypy pre-commit

# 3. Install the package in development mode
pip install -e .

# 4. Verify installation
python -c "import logveil; print(logveil.__version__)"
```

## Project Structure

```text
logveil/
├── cli/                    # Command-line interface
│   ├── args.py            # Argument parsing
│   ├── dispatcher.py      # Engine dispatch logic
│   └── logveil-agent.py   # Main CLI entry point
├── core/                   # Core processing engines
│   ├── redactor.py        # Python redaction engine
│   ├── profiles.py        # Profile management
│   ├── sanitizer.py       # Core sanitizer logic
│   ├── sanitizer_engine.rs # Rust performance engine
│   └── Cargo.toml         # Rust dependencies
├── bridge/                 # Language bridges
│   └── go-wrapper/        # Go concurrent processor
├── profiles/              # Built-in redaction profiles
│   ├── application.json   # Generic application logs
│   ├── nginx.json         # Nginx web server logs
│   └── docker.json        # Container logs
├── serve/                 # API server components
│   └── api.py            # REST API implementation
├── tests/                 # Test suite
│   ├── test_*.py         # Unit tests
│   └── fixtures/         # Test data
├── tools/                 # Development tools
│   └── testbench/        # Performance benchmarks
├── types/                 # Type definitions
│   └── models.py         # Data models
├── utils/                 # Utility functions
│   ├── error_handling.py # Error handling
│   ├── file_io.py        # File operations
│   └── logging.py        # Logging utilities
└── schemas/              # Configuration schemas
    ├── output_schema.json
    └── redaction_policy.yaml
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=logveil --cov-report=html

# Run specific test file
pytest tests/test_redactor.py

# Run tests with verbose output
pytest -v

# Run performance benchmarks
python tools/testbench/benchmark.py
```

### Writing Tests

- Place unit tests in `tests/` directory
- Use descriptive test names: `test_redactor_handles_ipv4_addresses`
- Include both positive and negative test cases
- Mock external dependencies
- Test error conditions and edge cases

Example test structure:

```python
import pytest
from logveil.core.redactor import RedactionEngine

class TestRedactionEngine:
    def setup_method(self):
        self.engine = RedactionEngine()
    
    def test_redacts_email_addresses(self):
        result = self.engine.redact_line("Contact: admin@example.com")
        assert "[REDACTED_EMAIL]" in result.sanitized_text
        assert "admin@example.com" not in result.sanitized_text
    
    def test_handles_empty_input(self):
        result = self.engine.redact_line("")
        assert result.sanitized_text == ""
```

## Code Standards

### Python Code Style

LogVeil follows PEP 8 with these specific requirements:

- Line length: 88 characters (Black default)
- Use type hints for all public functions
- Docstrings for all modules, classes, and public functions
- Import organization: standard library, third-party, local imports

```python
from typing import Optional, List, Dict
import logging

def redact_patterns(
    text: str, 
    patterns: List[str], 
    replacement: str = "[REDACTED]"
) -> str:
    """
    Apply redaction patterns to input text.
    
    Args:
        text: Input text to process
        patterns: List of regex patterns to match
        replacement: Replacement string for matches
        
    Returns:
        Text with sensitive patterns replaced
        
    Raises:
        ValueError: If patterns are invalid
    """
    # Implementation here
```

### Rust Code Style

- Follow `rustfmt` formatting
- Use `clippy` for linting
- Document all public functions
- Handle all error cases explicitly (no `unwrap()`)

```rust
/// Sanitize a line of text using compiled regex patterns
/// 
/// # Arguments
/// * `input` - The text to sanitize
/// * `patterns` - Map of pattern names to compiled regexes
/// 
/// # Returns
/// * `Result<String, SanitizeError>` - Sanitized text or error
pub fn sanitize_line(
    input: &str, 
    patterns: &HashMap<&str, Regex>
) -> Result<String, SanitizeError> {
    // Implementation with proper error handling
}
```

### Go Code Style

- Follow `gofmt` formatting
- Use `golint` for style checking
- Document exported functions
- Handle all error cases

```go
// ProcessLogFile sanitizes a log file using the specified engine
func ProcessLogFile(inputPath, outputPath string) (*ProcessResult, error) {
    // Validate inputs
    if inputPath == "" {
        return nil, errors.New("input path cannot be empty")
    }
    
    // Implementation with error handling
}
```

## Submitting Changes

### Pull Request Process

1. **Fork the repository** and create a feature branch
2. **Make your changes** following the code standards
3. **Add tests** for new functionality
4. **Update documentation** if needed
5. **Run the test suite** and ensure all tests pass
6. **Run linting tools**: `black`, `isort`, `mypy`, `cargo clippy`
7. **Submit a pull request** with a clear description

### Commit Messages

Use conventional commit format:

```text
type(scope): description

[optional body]

[optional footer]
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

Examples:

```text
feat(core): add entropy-based secret detection
fix(cli): handle missing profile files gracefully
docs(readme): update installation instructions
```

### Code Review Checklist

Before submitting, ensure:

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] No breaking changes (or properly documented)
- [ ] Performance impact is acceptable
- [ ] Security implications are considered

## Adding Profiles

Profiles are JSON files located in `profiles/`. To add a new profile:

1. **Create the profile file**:

```json
{
  "name": "new-profile",
  "description": "Description of the profile",
  "version": "1.0.0",
  "patterns": [
    {
      "name": "pattern_name",
      "pattern": "regex_pattern",
      "replacement": "[REDACTED_TYPE]",
      "enabled": true,
      "description": "What this pattern matches"
    }
  ],
  "entropy_config": {
    "enabled": true,
    "threshold": 4.5,
    "min_length": 8
  }
}
```

1. **Add tests** in `tests/test_profiles.py`:

```python
def test_new_profile_loads():
    manager = ProfileManager()
    profile = manager.get_profile("new-profile")
    assert profile is not None
    assert profile.name == "new-profile"
```

1. **Update documentation** in README.md

1. **Validate the profile**:

```bash
logveil profiles validate new-profile.json
```

## Performance Testing

### Benchmarking

Use the built-in benchmark tool:

```bash
# Run standard benchmarks
python tools/testbench/benchmark.py

# Test specific engine
python tools/testbench/benchmark.py --engine rust

# Custom test data
python tools/testbench/benchmark.py --input custom_logs/ --size 1GB
```

### Performance Guidelines

- New features should not degrade performance by more than 10%
- Memory usage should remain bounded for large files
- CPU usage should scale linearly with input size
- Include performance tests for new engines

### Profiling

```bash
# Profile Python code
python -m cProfile -o profile.stats cli/logveil-agent.py sample.log
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"

# Profile Rust code
cargo build --release
perf record --call-graph=dwarf target/release/logveil-engine
perf report
```

## Getting Help

- **Documentation**: Check the README and inline documentation
- **Issues**: Search existing GitHub issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Discord**: Join our development Discord server (link in README)

## Development Tips

### Debugging

```bash
# Enable debug logging
export LOGVEIL_LOG_LEVEL=DEBUG
logveil sanitize app.log

# Debug Rust components
RUST_LOG=debug cargo run

# Python debugging
python -m pdb cli/logveil-agent.py app.log
```

### IDE Setup

#### VS Code

Recommended extensions:

- Python
- Rust Analyzer
- Go
- GitLens

Settings (.vscode/settings.json):

```json
{
  "python.defaultInterpreter": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.mypyEnabled": true,
  "rust-analyzer.checkOnSave.command": "clippy"
}
```

#### PyCharm

- Enable type checking
- Configure code style to match Black
- Set up pytest as the test runner

### Common Issues

**ImportError when running tests**:

```bash
pip install -e .
```

**Rust compilation fails**:

```bash
rustup update
cargo clean && cargo build
```

**Go bridge not working**:

```bash
cd bridge/go-wrapper
go mod tidy
go build
```

## Release Process

1. Update version numbers in:
   - `pyproject.toml`
   - `__init__.py`
   - `Cargo.toml`

2. Update CHANGELOG.md

3. Create release tag:

```bash
git tag -a v2.0.1 -m "Release v2.0.1"
git push origin v2.0.1
```

1. GitHub Actions will automatically:
   - Run all tests
   - Build packages
   - Publish to PyPI
   - Create GitHub release

Thank you for contributing to LogVeil!
