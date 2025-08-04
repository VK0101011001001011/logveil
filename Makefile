# LogVeil Development Makefile
# 
# This Makefile provides common development tasks for LogVeil.
# Run 'make help' to see available targets.

.PHONY: help setup clean test lint format check-deps build install-dev
.DEFAULT_GOAL := help

# Configuration
PYTHON := python
PIP := pip
VENV_DIR := venv
SOURCE_DIRS := cli core serve types utils tests

help: ## Show this help message
	@echo "LogVeil Development Commands"
	@echo "==========================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Set up development environment
	@echo "Setting up LogVeil development environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Activating virtual environment and installing dependencies..."
	$(VENV_DIR)/Scripts/activate && $(PIP) install --upgrade pip setuptools wheel
	$(VENV_DIR)/Scripts/activate && $(PIP) install -e .[dev]
	$(VENV_DIR)/Scripts/activate && pre-commit install
	@echo "Setup complete! Activate with: $(VENV_DIR)\Scripts\activate"

setup-unix: ## Set up development environment (Unix/Linux/macOS)
	@echo "Setting up LogVeil development environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Activating virtual environment and installing dependencies..."
	$(VENV_DIR)/bin/activate && $(PIP) install --upgrade pip setuptools wheel
	$(VENV_DIR)/bin/activate && $(PIP) install -e .[dev]
	$(VENV_DIR)/bin/activate && pre-commit install
	@echo "Setup complete! Activate with: source $(VENV_DIR)/bin/activate"

clean: ## Clean build artifacts and cache files
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "Clean complete!"

test: ## Run all tests
	@echo "Running tests..."
	pytest

test-cov: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	pytest --cov=logveil --cov-report=html --cov-report=term

test-fast: ## Run tests without slow markers
	@echo "Running fast tests..."
	pytest -m "not slow"

lint: ## Run all linting tools
	@echo "Running linting tools..."
	black --check $(SOURCE_DIRS)
	isort --check-only $(SOURCE_DIRS)
	mypy $(SOURCE_DIRS)
	flake8 $(SOURCE_DIRS)

format: ## Format code with black and isort
	@echo "Formatting code..."
	black $(SOURCE_DIRS)
	isort $(SOURCE_DIRS)

check-deps: ## Check for dependency vulnerabilities
	@echo "Checking dependencies for vulnerabilities..."
	pip-audit
	safety check

build-rust: ## Build Rust components
	@echo "Building Rust components..."
	cd core && cargo build --release

build: ## Build all components
	@echo "Building LogVeil..."
	$(PYTHON) -m build

install-dev: ## Install in development mode
	@echo "Installing LogVeil in development mode..."
	$(PIP) install -e .[dev]

benchmark: ## Run performance benchmarks
	@echo "Running benchmarks..."
	$(PYTHON) tools/testbench/benchmark.py

docs: ## Generate documentation
	@echo "Generating documentation..."
	sphinx-build -b html docs/ docs/_build/html

validate: ## Validate configuration files
	@echo "Validating profiles..."
	$(PYTHON) -c "from core.profiles import ProfileManager; ProfileManager().validate_all()"

pre-commit: ## Run pre-commit hooks
	@echo "Running pre-commit hooks..."
	pre-commit run --all-files

ci: clean lint test ## Run CI pipeline locally
	@echo "CI pipeline complete!"

release-check: ## Check if ready for release
	@echo "Checking release readiness..."
	$(PYTHON) -c "import logveil; print(f'Version: {logveil.__version__}')"
	@echo "Running full test suite..."
	pytest
	@echo "Running security checks..."
	pip-audit
	@echo "Ready for release!"

dev-server: ## Start development API server
	@echo "Starting development server..."
	$(PYTHON) -m logveil serve --host 127.0.0.1 --port 8080 --debug

# Platform-specific targets
ifeq ($(OS),Windows_NT)
    SHELL_ACTIVATE := $(VENV_DIR)\Scripts\activate
    ENV_SETUP := setup
else
    SHELL_ACTIVATE := source $(VENV_DIR)/bin/activate
    ENV_SETUP := setup-unix
endif

quick-start: $(ENV_SETUP) ## One-command setup for new contributors
	@echo "LogVeil is ready for development!"
	@echo "Next steps:"
	@echo "  1. Activate environment: $(SHELL_ACTIVATE)"
	@echo "  2. Run tests: make test"
	@echo "  3. Start coding!"

# Docker targets
docker-build: ## Build Docker image
	@echo "Building Docker image..."
	docker build -t logveil:dev .

docker-test: ## Run tests in Docker
	@echo "Running tests in Docker..."
	docker run --rm logveil:dev pytest

# Maintenance targets
update-deps: ## Update all dependencies
	@echo "Updating dependencies..."
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install --upgrade -r requirements.txt
	pre-commit autoupdate

# Security targets  
security-scan: ## Run security scans
	@echo "Running security scans..."
	bandit -r $(SOURCE_DIRS)
	semgrep --config=auto $(SOURCE_DIRS)

# Performance targets
profile: ## Profile the application
	@echo "Profiling LogVeil..."
	$(PYTHON) -m cProfile -o profile.stats cli/logveil-agent.py sample_log.txt
	$(PYTHON) -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"

memory-profile: ## Memory profiling
	@echo "Memory profiling..."
	$(PYTHON) -m memory_profiler cli/logveil-agent.py sample_log.txt
