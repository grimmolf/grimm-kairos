# Kairos Cross-Platform Build System
# Replaces Windows-only .bat files with universal Makefile
# Follows pure-bash-bible principles for maximum compatibility

# Configuration
PYTHON ?= python3
PIP ?= pip3
BUILD_DIR = build
DIST_DIR = dist
VENV_DIR = venv

# Detect OS for platform-specific commands
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    OS = linux
    OPEN = xdg-open
endif
ifeq ($(UNAME_S),Darwin)
    OS = macos
    OPEN = open
endif
ifeq ($(OS),Windows_NT)
    OS = windows
    OPEN = start
endif

# Colors for output (using ANSI codes)
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

# Help target
.PHONY: help
help: ## Show this help message
	@echo "$(GREEN)Kairos Build System$(NC)"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Environment setup
.PHONY: venv
venv: ## Create virtual environment
	@echo "$(YELLOW)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "$(GREEN)Virtual environment created. Activate with: source $(VENV_DIR)/bin/activate$(NC)"

.PHONY: install-deps
install-deps: ## Install dependencies
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Dependencies installed$(NC)"

.PHONY: install-modern-deps
install-modern-deps: ## Install modernized dependencies
	@echo "$(YELLOW)Installing modern dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements_modern.txt
	@echo "$(GREEN)Modern dependencies installed$(NC)"

# Development setup
.PHONY: dev-setup
dev-setup: venv install-modern-deps ## Complete development setup
	@echo "$(GREEN)Development environment ready!$(NC)"
	@echo "Run: source $(VENV_DIR)/bin/activate"

# Build targets
.PHONY: build
build: clean ## Build Kairos package
	@echo "$(YELLOW)Building Kairos...$(NC)"
	./build.sh
	@echo "$(GREEN)Build completed$(NC)"

.PHONY: build-dev
build-dev: clean ## Build in development mode
	@echo "$(YELLOW)Building Kairos in development mode...$(NC)"
	BUILD_TYPE=dev ./build.sh
	@echo "$(GREEN)Development build completed$(NC)"

.PHONY: build-cython
build-cython: ## Build with Cython extensions
	@echo "$(YELLOW)Building Cython extensions...$(NC)"
	@if [ -f cython.py ]; then \
		cp setup.py _setup.py; \
		cp cython.py setup.py; \
		$(PYTHON) setup.py build_ext --inplace; \
		mv setup.py cython.py; \
		mv _setup.py setup.py; \
		echo "$(GREEN)Cython build completed$(NC)"; \
	else \
		echo "$(RED)cython.py not found$(NC)"; \
		exit 1; \
	fi

# Installation targets
.PHONY: install
install: ## Install Kairos package
	@echo "$(YELLOW)Installing Kairos...$(NC)"
	$(PIP) install .
	@echo "$(GREEN)Kairos installed$(NC)"

.PHONY: install-editable
install-editable: ## Install in editable/development mode
	@echo "$(YELLOW)Installing Kairos in editable mode...$(NC)"
	$(PIP) install -e .
	@echo "$(GREEN)Kairos installed in editable mode$(NC)"

# Testing targets
.PHONY: test
test: ## Run tests
	@echo "$(YELLOW)Running tests...$(NC)"
	@if command -v pytest >/dev/null 2>&1; then \
		pytest; \
	else \
		$(PYTHON) -m unittest discover -s tests -p "*test*.py"; \
	fi
	@echo "$(GREEN)Tests completed$(NC)"

.PHONY: test-verbose
test-verbose: ## Run tests with verbose output
	@echo "$(YELLOW)Running tests (verbose)...$(NC)"
	@if command -v pytest >/dev/null 2>&1; then \
		pytest -v; \
	else \
		$(PYTHON) -m unittest discover -s tests -p "*test*.py" -v; \
	fi

# Code quality targets
.PHONY: lint
lint: ## Run linting
	@echo "$(YELLOW)Running linting...$(NC)"
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 kairos/ tv/ --max-line-length=120; \
	else \
		echo "$(YELLOW)flake8 not installed, skipping lint$(NC)"; \
	fi

.PHONY: format
format: ## Format code with black
	@echo "$(YELLOW)Formatting code...$(NC)"
	@if command -v black >/dev/null 2>&1; then \
		black kairos/ tv/ --line-length=120; \
		echo "$(GREEN)Code formatted$(NC)"; \
	else \
		echo "$(YELLOW)black not installed, skipping format$(NC)"; \
	fi

.PHONY: type-check
type-check: ## Run type checking
	@echo "$(YELLOW)Running type checking...$(NC)"
	@if command -v mypy >/dev/null 2>&1; then \
		mypy kairos/ tv/ --ignore-missing-imports; \
	else \
		echo "$(YELLOW)mypy not installed, skipping type check$(NC)"; \
	fi

# Cleanup targets
.PHONY: clean
clean: ## Clean build artifacts
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	rm -rf $(BUILD_DIR)/ $(DIST_DIR)/ Kairos.egg-info/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.so" -delete 2>/dev/null || true
	find . -type f -name "*.c" -name "*_wrap*" -delete 2>/dev/null || true
	@echo "$(GREEN)Cleanup completed$(NC)"

.PHONY: clean-all
clean-all: clean ## Clean everything including virtual environment
	@echo "$(YELLOW)Cleaning everything...$(NC)"
	rm -rf $(VENV_DIR)/
	rm -rf log/
	rm -rf screenshots/
	@echo "$(GREEN)Deep cleanup completed$(NC)"

# Documentation targets
.PHONY: docs
docs: ## Generate documentation
	@echo "$(YELLOW)Generating documentation...$(NC)"
	@if command -v sphinx-build >/dev/null 2>&1; then \
		sphinx-build -b html docs/ docs/_build/; \
		echo "$(GREEN)Documentation generated$(NC)"; \
	else \
		echo "$(YELLOW)Sphinx not installed, skipping docs$(NC)"; \
	fi

.PHONY: open-docs
open-docs: docs ## Open documentation in browser
	$(OPEN) docs/_build/index.html

# Distribution targets
.PHONY: dist
dist: clean ## Create distribution package
	@echo "$(YELLOW)Creating distribution...$(NC)"
	$(PYTHON) setup.py sdist bdist_wheel
	@echo "$(GREEN)Distribution created in $(DIST_DIR)/$(NC)"

.PHONY: upload-test
upload-test: dist ## Upload to test PyPI
	@echo "$(YELLOW)Uploading to test PyPI...$(NC)"
	@if command -v twine >/dev/null 2>&1; then \
		twine upload --repository testpypi $(DIST_DIR)/*; \
	else \
		echo "$(RED)twine not installed$(NC)"; \
		exit 1; \
	fi

.PHONY: upload
upload: dist ## Upload to PyPI
	@echo "$(YELLOW)Uploading to PyPI...$(NC)"
	@if command -v twine >/dev/null 2>&1; then \
		twine upload $(DIST_DIR)/*; \
	else \
		echo "$(RED)twine not installed$(NC)"; \
		exit 1; \
	fi

# Migration targets
.PHONY: migrate-deps
migrate-deps: ## Migrate to modern dependencies
	@echo "$(YELLOW)Migrating to modern dependencies...$(NC)"
	cp setup.cfg setup.cfg.backup
	cp setup_modern.cfg setup.cfg
	cp requirements.txt requirements.txt.backup
	cp requirements_modern.txt requirements.txt
	@echo "$(GREEN)Dependencies migrated (backups created)$(NC)"

.PHONY: rollback-deps
rollback-deps: ## Rollback dependency migration
	@echo "$(YELLOW)Rolling back dependency migration...$(NC)"
	@if [ -f setup.cfg.backup ]; then \
		mv setup.cfg.backup setup.cfg; \
		echo "$(GREEN)setup.cfg restored$(NC)"; \
	fi
	@if [ -f requirements.txt.backup ]; then \
		mv requirements.txt.backup requirements.txt; \
		echo "$(GREEN)requirements.txt restored$(NC)"; \
	fi

# Utility targets
.PHONY: check-deps
check-deps: ## Check for outdated dependencies
	@echo "$(YELLOW)Checking for outdated dependencies...$(NC)"
	$(PIP) list --outdated

.PHONY: security-check
security-check: ## Run security checks
	@echo "$(YELLOW)Running security checks...$(NC)"
	@if command -v safety >/dev/null 2>&1; then \
		safety check; \
	else \
		echo "$(YELLOW)safety not installed, skipping security check$(NC)"; \
	fi

.PHONY: requirements
requirements: ## Generate requirements.txt from current environment
	@echo "$(YELLOW)Generating requirements.txt...$(NC)"
	$(PIP) freeze > requirements_generated.txt
	@echo "$(GREEN)Requirements saved to requirements_generated.txt$(NC)"

# Run targets
.PHONY: run
run: ## Run Kairos with default settings
	@echo "$(YELLOW)Running Kairos...$(NC)"
	$(PYTHON) main.py

.PHONY: run-help
run-help: ## Show Kairos help
	$(PYTHON) main.py -h

# Development workflow
.PHONY: dev-workflow
dev-workflow: clean install-modern-deps build-dev test lint ## Complete development workflow
	@echo "$(GREEN)Development workflow completed successfully!$(NC)"

# CI/CD targets
.PHONY: ci
ci: clean install-modern-deps build test lint type-check ## CI pipeline
	@echo "$(GREEN)CI pipeline completed$(NC)"

# Platform-specific targets
.PHONY: linux-deps
linux-deps: ## Install Linux-specific dependencies
ifeq ($(OS),linux)
	@echo "$(YELLOW)Installing Linux dependencies...$(NC)"
	$(PIP) install pyvirtualdisplay
	@echo "$(GREEN)Linux dependencies installed$(NC)"
else
	@echo "$(YELLOW)Not running on Linux, skipping$(NC)"
endif

.PHONY: macos-deps
macos-deps: ## Install macOS-specific dependencies
ifeq ($(OS),macos)
	@echo "$(YELLOW)Installing macOS dependencies...$(NC)"
	$(PIP) install pyobjc-core pyobjc
	@echo "$(GREEN)macOS dependencies installed$(NC)"
else
	@echo "$(YELLOW)Not running on macOS, skipping$(NC)"
endif

# Information targets
.PHONY: info
info: ## Show system information
	@echo "$(GREEN)System Information:$(NC)"
	@echo "OS: $(OS)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Pip: $(shell $(PIP) --version)"
	@echo "Build Dir: $(BUILD_DIR)"
	@echo "Dist Dir: $(DIST_DIR)"

.PHONY: version
version: ## Show Kairos version
	@echo "$(GREEN)Kairos Version:$(NC)"
	@$(PYTHON) -c "import configparser; c=configparser.ConfigParser(); c.read('setup.cfg'); print(c.get('metadata', 'version'))"

# Modernization targets
.PHONY: modernize
modernize: migrate-deps install-modern-deps build-dev test ## Complete modernization process
	@echo "$(GREEN)Modernization completed!$(NC)"
	@echo "$(YELLOW)New features:$(NC)"
	@echo "  - Modern Google Auth (replaces oauth2client)"
	@echo "  - Selenium 4+ WebDriver management"
	@echo "  - Built-in anti-detection (replaces selenium-stealth)"
	@echo "  - Modular architecture"
	@echo "  - Cross-platform build system"