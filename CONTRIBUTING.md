# Contributing to LogVeil

Thank you for your interest in contributing to LogVeil! This guide will help you get started with development, testing, and extending the platform.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/logveil/logveil.git
   cd logveil
   ```

2. Install dependencies in a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Running Tests

Run the full test suite with:
```bash
pytest
```

For coverage report:
```bash
pytest --cov=sanilog
```

## Adding Profiles

Profiles are JSON files located in `sanilog/profiles/`. To add a new profile:

1. Create a new JSON file following the existing profile format.
2. Add the profile to the list in the documentation if applicable.
3. Write tests to cover the new profile's redaction rules.

## Integrating Plugins

LogVeil supports Python and WASM plugins:

- Place Python plugins in `sanilog/plugins/`.
- WASM plugins require a compatible runtime; see the WASM documentation.
- Register plugins via configuration files or CLI options.

## CI/CD Pipeline

The project uses GitHub Actions for CI:

- Tests run on push and pull requests.
- Pre-commit hooks enforce code style and linting.
- Benchmarks and coverage reports are generated.

To run CI locally, use:
```bash
pre-commit run --all-files
pytest
```

## Code Style

- Follow PEP 8 for Python code.
- Use type hints consistently.
- Write clear, descriptive docstrings.

## Reporting Issues and Pull Requests

- Use GitHub Issues for bug reports and feature requests.
- Fork the repo and submit pull requests for contributions.
- Ensure all tests pass before submitting.

Thank you for helping improve LogVeil!