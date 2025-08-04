#!/usr/bin/env pwsh
<#
.SYNOPSIS
    LogVeil Development Setup Script for Windows

.DESCRIPTION
    This script sets up the LogVeil development environment on Windows.
    It creates a virtual environment, installs dependencies, and configures
    development tools.

.PARAMETER SkipVenv
    Skip virtual environment creation (use system Python)

.PARAMETER DevMode
    Install additional development dependencies

.PARAMETER QuickSetup
    Run minimal setup without optional components

.EXAMPLE
    .\setup.ps1
    Standard setup with virtual environment

.EXAMPLE
    .\setup.ps1 -DevMode
    Setup with additional development tools

.EXAMPLE
    .\setup.ps1 -QuickSetup
    Minimal setup for quick testing
#>

param(
    [switch]$SkipVenv,
    [switch]$DevMode,
    [switch]$QuickSetup
)

# Configuration
$ErrorActionPreference = "Stop"
$VenvDir = "venv"

# Colors for output
$ColorGreen = "Green"
$ColorYellow = "Yellow"
$ColorRed = "Red"
$ColorBlue = "Blue"

function Write-Status {
    param([string]$Message, [string]$Color = "Blue")
    Write-Host "🔧 $Message" -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $ColorGreen
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $ColorYellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $ColorRed
}

function Test-PythonVersion {
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            if ($major -eq 3 -and $minor -ge 8) {
                Write-Success "Python $($matches[0]) found"
                return $true
            }
        }
        Write-Error "Python 3.8+ required, found: $pythonVersion"
        return $false
    }
    catch {
        Write-Error "Python not found in PATH"
        return $false
    }
}

function New-VirtualEnvironment {
    if ($SkipVenv) {
        Write-Warning "Skipping virtual environment creation"
        return
    }

    Write-Status "Creating virtual environment..."
    if (Test-Path $VenvDir) {
        Write-Warning "Virtual environment already exists, removing..."
        Remove-Item -Recurse -Force $VenvDir
    }
    
    python -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create virtual environment"
    }
    Write-Success "Virtual environment created"
}

function Install-Dependencies {
    Write-Status "Installing dependencies..."
    
    if (-not $SkipVenv) {
        & "$VenvDir\Scripts\Activate.ps1"
    }

    # Upgrade pip and core tools
    python -m pip install --upgrade pip setuptools wheel
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to upgrade pip"
    }

    # Install base requirements
    if (Test-Path "requirements.txt") {
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install requirements"
        }
    }

    # Install package in development mode
    pip install -e .
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install LogVeil"
    }

    # Install development dependencies
    if ($DevMode -or -not $QuickSetup) {
        Write-Status "Installing development dependencies..."
        pip install pytest pytest-cov black isort mypy flake8 pre-commit
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Some development dependencies failed to install"
        }
    }

    Write-Success "Dependencies installed"
}

function Install-PreCommitHooks {
    if ($QuickSetup) {
        Write-Warning "Skipping pre-commit hooks (quick setup)"
        return
    }

    try {
        Write-Status "Installing pre-commit hooks..."
        pre-commit install
        Write-Success "Pre-commit hooks installed"
    }
    catch {
        Write-Warning "Failed to install pre-commit hooks"
    }
}

function Test-Installation {
    Write-Status "Testing installation..."
    
    try {
        python -c "import logveil; print(f'LogVeil {logveil.__version__} installed successfully')"
        Write-Success "LogVeil imported successfully"
    }
    catch {
        Write-Error "Failed to import LogVeil"
        throw
    }

    if (-not $QuickSetup) {
        Write-Status "Running basic tests..."
        python -m pytest tests/ -x --tb=short
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Basic tests passed"
        } else {
            Write-Warning "Some tests failed, but installation appears successful"
        }
    }
}

function Show-NextSteps {
    Write-Host ""
    Write-Host "🎉 LogVeil development environment setup complete!" -ForegroundColor $ColorGreen
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor $ColorBlue
    
    if (-not $SkipVenv) {
        Write-Host "  1. Activate virtual environment:" -ForegroundColor $ColorBlue
        Write-Host "     $VenvDir\Scripts\Activate.ps1" -ForegroundColor White
    }
    
    Write-Host "  2. Run tests:" -ForegroundColor $ColorBlue
    Write-Host "     pytest" -ForegroundColor White
    
    Write-Host "  3. Try the CLI:" -ForegroundColor $ColorBlue
    Write-Host "     python cli/logveil-agent.py sample_log.txt" -ForegroundColor White
    
    Write-Host "  4. Start development server:" -ForegroundColor $ColorBlue
    Write-Host "     python -m logveil serve" -ForegroundColor White

    Write-Host ""
    Write-Host "Development commands:" -ForegroundColor $ColorBlue
    Write-Host "  Format code:    black ." -ForegroundColor White
    Write-Host "  Run linting:    flake8 ." -ForegroundColor White
    Write-Host "  Type checking:  mypy ." -ForegroundColor White
    Write-Host "  Run benchmarks: python tools/testbench/benchmark.py" -ForegroundColor White
    Write-Host ""
}

# Main execution
try {
    Write-Host "LogVeil Development Setup" -ForegroundColor $ColorBlue
    Write-Host "========================" -ForegroundColor $ColorBlue
    Write-Host ""

    # Check prerequisites
    if (-not (Test-PythonVersion)) {
        Write-Host "Please install Python 3.8+ and add it to PATH"
        exit 1
    }

    # Check if Git is available
    try {
        git --version | Out-Null
        Write-Success "Git found"
    }
    catch {
        Write-Warning "Git not found - some features may not work"
    }

    # Setup steps
    New-VirtualEnvironment
    Install-Dependencies
    Install-PreCommitHooks
    Test-Installation
    Show-NextSteps

    Write-Success "Setup completed successfully!"
}
catch {
    Write-Error "Setup failed: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Troubleshooting tips:" -ForegroundColor $ColorYellow
    Write-Host "  - Ensure Python 3.8+ is installed and in PATH"
    Write-Host "  - Run PowerShell as Administrator if permission issues occur"
    Write-Host "  - Check internet connection for package downloads"
    Write-Host "  - Try running with -QuickSetup for minimal installation"
    exit 1
}
