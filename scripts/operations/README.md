# Operations Module

Unified execution pipeline for OS Dashboard AI Assistant operations.

## Overview

This module provides a structured, reusable system for performing common operations:
- **Install**: Install dependencies (Python, frontend, virtual environment)
- **Build**: Build frontend and executables
- **Test**: Run tests (unit, integration, E2E, frontend, backend)
- **Launch**: Launch the application in various modes
- **Verify**: Verify installation, builds, and health

## Architecture

### Base Classes

- `BaseOperation`: Base class for all operations with common utilities
- `OperationResult`: Standardized result structure
- `OperationStatus`: Status enumeration (SUCCESS, FAILED, SKIPPED, WARNING)

### Operation Classes

- `InstallOperation`: Handles installation of dependencies
- `BuildOperation`: Handles building of frontend and executables
- `TestOperation`: Handles test execution
- `LaunchOperation`: Handles launching the application
- `VerifyOperation`: Handles verification and health checks

## Usage

### Command Line

```bash
# Using the main script
python scripts/execute.py install
python scripts/execute.py build --target web
python scripts/execute.py test --type all
python scripts/execute.py launch --mode web
python scripts/execute.py verify

# Using the convenience wrapper (from project root)
python run.py install
python run.py build --target web
python run.py pipeline  # Run full pipeline
```

### Programmatic Usage

```python
from scripts.operations import InstallOperation, BuildOperation

# Install
install_op = InstallOperation(verbose=True)
result = install_op.execute(create_venv=True, install_python=True, install_frontend=True)
if result.success:
    print("Installation successful!")

# Build
build_op = BuildOperation(verbose=True)
result = build_op.execute(target="web", install_deps=True)
if result.success:
    print(f"Build output: {result.details}")
```

## Commands

### Install

```bash
python scripts/execute.py install [options]

Options:
  --no-venv        Don't create virtual environment
  --no-python      Don't install Python dependencies
  --no-frontend    Don't install frontend dependencies
  --package        Install Python package itself
  --force-venv     Force recreation of virtual environment
```

### Build

```bash
python scripts/execute.py build [options]

Options:
  --target TARGET  Build target: web, desktop:linux, desktop:windows, desktop:mac, desktop:all, all
  --no-deps        Don't install dependencies before building
  --executable     Also build Python executable
```

### Test

```bash
python scripts/execute.py test [options]

Options:
  --type TYPE      Test type: all, unit, integration, e2e, frontend, backend, smoke, regression
  --coverage       Generate coverage reports
  --env ENV        Test environment (for E2E tests)
  --markers MARK   Pytest markers (can specify multiple)
```

### Launch

```bash
python scripts/execute.py launch [options]

Options:
  --mode MODE      Launch mode: web, desktop, web-build, desktop-build, orchestrator, backend-only
  --workspace DIR  Workspace root (for orchestrator)
  --host HOST      Backend host (default: 127.0.0.1)
  --port PORT      Backend port (default: 8000)
  --reload         Enable auto-reload
  --ui             Enable UI (for orchestrator)
```

### Verify

```bash
python scripts/execute.py verify [options]

Options:
  --no-installation   Skip installation check
  --backend           Check backend health
  --frontend-build    Check frontend build
  --no-structure      Skip structure check
  --backend-url URL   Backend URL (default: http://127.0.0.1:8000)
```

### Pipeline

```bash
python scripts/execute.py pipeline [options]

Runs full pipeline: install -> build -> test -> verify

Options:
  --skip-install    Skip installation step
  --skip-build      Skip build step
  --skip-test       Skip test step
  --skip-verify     Skip verify step
  --build-target    Build target (default: web)
```

## Extension

To add a new operation:

1. Create a new class inheriting from `BaseOperation`
2. Implement `execute()` method
3. Optionally override `check_prerequisites()`
4. Return `OperationResult` objects
5. Add command to `scripts/execute.py`
6. Export from `scripts/operations/__init__.py`

## Best Practices

1. **Error Handling**: Always use `OperationResult` to return results, don't raise exceptions unless critical
2. **Logging**: Use `self.logger` for consistent logging
3. **Prerequisites**: Check prerequisites in `check_prerequisites()` method
4. **Timeouts**: Use appropriate timeouts for long-running operations
5. **Details**: Include useful details in `OperationResult.details` dictionary
6. **Status Codes**: Return appropriate exit codes (0 for success, non-zero for failure)

## Examples

### Full Development Setup

```bash
# Install everything
python run.py install

# Build web version
python run.py build --target web

# Run tests
python run.py test --type all --coverage

# Verify setup
python run.py verify --backend --frontend-build

# Launch development server
python run.py launch --mode web --reload
```

### CI/CD Pipeline

```bash
# Run full pipeline with all checks
python run.py pipeline --build-target web
```

### Quick Start

```bash
# One command to install, build, test, and verify
python run.py pipeline
```

