#!/bin/bash
# LogVeil Development Setup Script
# 
# This script sets up the LogVeil development environment on Unix-like systems.
# It creates a virtual environment, installs dependencies, and configures
# development tools.

set -euo pipefail

# Configuration
VENV_DIR="venv"
PYTHON_MIN_VERSION="3.8"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Options
SKIP_VENV=false
DEV_MODE=false
QUICK_SETUP=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-venv)
            SKIP_VENV=true
            shift
            ;;
        --dev-mode)
            DEV_MODE=true
            shift
            ;;
        --quick-setup)
            QUICK_SETUP=true
            shift
            ;;
        --help)
            echo "LogVeil Development Setup Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --skip-venv      Skip virtual environment creation"
            echo "  --dev-mode       Install additional development dependencies"
            echo "  --quick-setup    Run minimal setup without optional components"
            echo "  --help           Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Utility functions
log_status() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

log_success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

log_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python_version() {
    if ! command_exists python3; then
        log_error "Python 3 not found. Please install Python 3.8+"
        return 1
    fi

    local python_version
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    
    if [[ $(echo "$python_version >= $PYTHON_MIN_VERSION" | bc -l) -eq 1 ]]; then
        log_success "Python $python_version found"
        return 0
    else
        log_error "Python $PYTHON_MIN_VERSION+ required, found: $python_version"
        return 1
    fi
}

# Create virtual environment
create_virtual_environment() {
    if [[ "$SKIP_VENV" == true ]]; then
        log_warning "Skipping virtual environment creation"
        return 0
    fi

    log_status "Creating virtual environment..."
    
    if [[ -d "$VENV_DIR" ]]; then
        log_warning "Virtual environment already exists, removing..."
        rm -rf "$VENV_DIR"
    fi
    
    python3 -m venv "$VENV_DIR"
    log_success "Virtual environment created"
}

# Install dependencies
install_dependencies() {
    log_status "Installing dependencies..."
    
    # Activate virtual environment if not skipped
    if [[ "$SKIP_VENV" == false ]]; then
        # shellcheck source=/dev/null
        source "$VENV_DIR/bin/activate"
    fi

    # Upgrade pip and core tools
    python3 -m pip install --upgrade pip setuptools wheel

    # Install base requirements
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
    fi

    # Install package in development mode
    pip install -e .

    # Install development dependencies
    if [[ "$DEV_MODE" == true ]] || [[ "$QUICK_SETUP" == false ]]; then
        log_status "Installing development dependencies..."
        pip install pytest pytest-cov black isort mypy flake8 pre-commit bandit safety || {
            log_warning "Some development dependencies failed to install"
        }
    fi

    log_success "Dependencies installed"
}

# Install pre-commit hooks
install_pre_commit_hooks() {
    if [[ "$QUICK_SETUP" == true ]]; then
        log_warning "Skipping pre-commit hooks (quick setup)"
        return 0
    fi

    if command_exists pre-commit; then
        log_status "Installing pre-commit hooks..."
        pre-commit install || {
            log_warning "Failed to install pre-commit hooks"
        }
        log_success "Pre-commit hooks installed"
    else
        log_warning "pre-commit not available, skipping hooks"
    fi
}

# Test installation
test_installation() {
    log_status "Testing installation..."
    
    python3 -c "import logveil; print(f'LogVeil {logveil.__version__} installed successfully')" || {
        log_error "Failed to import LogVeil"
        return 1
    }
    log_success "LogVeil imported successfully"

    if [[ "$QUICK_SETUP" == false ]]; then
        log_status "Running basic tests..."
        if python3 -m pytest tests/ -x --tb=short; then
            log_success "Basic tests passed"
        else
            log_warning "Some tests failed, but installation appears successful"
        fi
    fi
}

# Show next steps
show_next_steps() {
    echo ""
    echo -e "${GREEN}[SUCCESS] LogVeil development environment setup complete!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    
    if [[ "$SKIP_VENV" == false ]]; then
        echo -e "${BLUE}  1. Activate virtual environment:${NC}"
        echo -e "     source $VENV_DIR/bin/activate"
    fi
    
    echo -e "${BLUE}  2. Run tests:${NC}"
    echo -e "     pytest"
    
    echo -e "${BLUE}  3. Try the CLI:${NC}"
    echo -e "     python -m logveil.cli.logveil_agent examples/sample_log.txt"
    
    echo -e "${BLUE}  4. Start development server:${NC}"
    echo -e "     python -m logveil serve"

    echo ""
    echo -e "${BLUE}Development commands:${NC}"
    echo -e "  Format code:    black ."
    echo -e "  Run linting:    flake8 ."
    echo -e "  Type checking:  mypy ."
    echo -e "  Security scan:  bandit -r ."
    echo -e "  Run benchmarks: python tools/testbench/benchmark.py"
    echo ""
}

# Check if we need to install bc for version comparison
ensure_bc() {
    if ! command_exists bc; then
        log_warning "bc not found, using alternative version check"
        # Alternative version check using Python
        check_python_version() {
            if ! command_exists python3; then
                log_error "Python 3 not found. Please install Python 3.8+"
                return 1
            fi

            if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
                local python_version
                python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
                log_success "Python $python_version found"
                return 0
            else
                local python_version
                python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
                log_error "Python $PYTHON_MIN_VERSION+ required, found: $python_version"
                return 1
            fi
        }
    fi
}

# Main execution
main() {
    echo -e "${BLUE}LogVeil Development Setup${NC}"
    echo -e "${BLUE}========================${NC}"
    echo ""

    # Change to script directory
    cd "$SCRIPT_DIR"

    # Check prerequisites
    ensure_bc
    check_python_version || exit 1

    # Check if Git is available
    if command_exists git; then
        log_success "Git found"
    else
        log_warning "Git not found - some features may not work"
    fi

    # Check if we're in a Git repository
    if [[ -d ".git" ]]; then
        log_success "Git repository detected"
    else
        log_warning "Not in a Git repository - pre-commit hooks may not work"
    fi

    # Setup steps
    create_virtual_environment
    install_dependencies
    install_pre_commit_hooks
    test_installation
    show_next_steps

    log_success "Setup completed successfully!"
}

# Error handling
trap 'log_error "Setup failed at line $LINENO. Exit code: $?"' ERR

# Run main function
main "$@"
