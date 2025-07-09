#!/bin/bash
# Modern cross-platform build script for Kairos
# Replaces Windows-only build_public.bat with POSIX-compliant version
# Follows pure-bash-bible principles for portability and efficiency

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Color output for better UX
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# Script directory for relative paths
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$SCRIPT_DIR"

# Configuration
readonly PYTHON_CMD="${PYTHON:-python3}"
readonly BUILD_TYPE="${BUILD_TYPE:-release}"
readonly VERBOSE="${VERBOSE:-false}"

# Logging functions (pure bash, no external dependencies)
log_info() {
    printf "${GREEN}[INFO]${NC} %s\n" "$*" >&2
}

log_warn() {
    printf "${YELLOW}[WARN]${NC} %s\n" "$*" >&2
}

log_error() {
    printf "${RED}[ERROR]${NC} %s\n" "$*" >&2
}

# Error handling
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_error "Build failed with exit code $exit_code"
        # Restore original setup.py if backup exists
        if [[ -f "${PROJECT_ROOT}/_setup.py" ]]; then
            mv "${PROJECT_ROOT}/_setup.py" "${PROJECT_ROOT}/setup.py"
            log_info "Restored original setup.py"
        fi
    fi
    exit $exit_code
}

trap cleanup EXIT

# Validation functions
check_requirements() {
    log_info "Checking build requirements..."
    
    # Check Python version
    if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
        log_error "Python not found. Please install Python 3.10+ or set PYTHON variable"
        return 1
    fi
    
    local python_version
    python_version=$("$PYTHON_CMD" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    
    if [[ $(echo "$python_version >= 3.10" | bc -l 2>/dev/null || echo "0") -eq 0 ]]; then
        # Fallback version check without bc
        local major minor
        IFS='.' read -r major minor <<< "$python_version"
        if [[ $major -lt 3 ]] || [[ $major -eq 3 && $minor -lt 10 ]]; then
            log_error "Python 3.10+ required, found $python_version"
            return 1
        fi
    fi
    
    log_info "Python $python_version found"
    
    # Check for required files
    local required_files=("setup.py" "cython.py" "requirements.txt")
    for file in "${required_files[@]}"; do
        if [[ ! -f "${PROJECT_ROOT}/$file" ]]; then
            log_error "Required file not found: $file"
            return 1
        fi
    done
    
    return 0
}

# Build functions using pure bash principles
backup_setup_file() {
    log_info "Backing up setup.py..."
    if [[ -f "${PROJECT_ROOT}/setup.py" ]]; then
        cp "${PROJECT_ROOT}/setup.py" "${PROJECT_ROOT}/_setup.py"
    fi
}

prepare_cython_build() {
    log_info "Preparing Cython build..."
    
    # Swap setup files (pure bash file operations)
    if [[ -f "${PROJECT_ROOT}/cython.py" ]]; then
        mv "${PROJECT_ROOT}/setup.py" "${PROJECT_ROOT}/_setup.py"
        mv "${PROJECT_ROOT}/cython.py" "${PROJECT_ROOT}/setup.py"
        log_info "Switched to Cython setup configuration"
    else
        log_warn "cython.py not found, using standard setup.py"
    fi
}

build_cython_extensions() {
    log_info "Building Cython extensions..."
    
    cd "$PROJECT_ROOT"
    
    if [[ "$VERBOSE" == "true" ]]; then
        "$PYTHON_CMD" setup.py build_ext --inplace
    else
        "$PYTHON_CMD" setup.py build_ext --inplace >/dev/null 2>&1
    fi
    
    log_info "Cython extensions built successfully"
}

restore_setup_files() {
    log_info "Restoring original setup files..."
    
    # Restore original setup.py
    if [[ -f "${PROJECT_ROOT}/_setup.py" ]]; then
        mv "${PROJECT_ROOT}/setup.py" "${PROJECT_ROOT}/cython.py"
        mv "${PROJECT_ROOT}/_setup.py" "${PROJECT_ROOT}/setup.py"
        log_info "Restored original setup configuration"
    fi
}

install_package() {
    log_info "Installing Kairos package..."
    
    cd "$PROJECT_ROOT"
    
    # Install in development mode for faster iteration
    if [[ "$BUILD_TYPE" == "dev" ]]; then
        "$PYTHON_CMD" -m pip install -e .
        log_info "Installed in development mode"
    else
        "$PYTHON_CMD" -m pip install .
        log_info "Installed in production mode"
    fi
}

run_cleanup() {
    log_info "Cleaning up build artifacts..."
    
    # Remove build directories (pure bash)
    local cleanup_dirs=("build" "dist" "Kairos.egg-info" "__pycache__")
    for dir in "${cleanup_dirs[@]}"; do
        if [[ -d "${PROJECT_ROOT}/$dir" ]]; then
            rm -rf "${PROJECT_ROOT:?}/$dir"
            [[ "$VERBOSE" == "true" ]] && log_info "Removed $dir"
        fi
    done
    
    # Remove compiled Python files
    find "$PROJECT_ROOT" -name "*.pyc" -type f -delete 2>/dev/null || true
    find "$PROJECT_ROOT" -name "*.pyo" -type f -delete 2>/dev/null || true
    find "$PROJECT_ROOT" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    log_info "Cleanup completed"
}

update_dependencies() {
    log_info "Updating dependencies..."
    
    # Use modern requirements if available
    local req_file="${PROJECT_ROOT}/requirements.txt"
    if [[ -f "${PROJECT_ROOT}/requirements_modern.txt" ]]; then
        req_file="${PROJECT_ROOT}/requirements_modern.txt"
        log_info "Using modernized dependencies"
    fi
    
    "$PYTHON_CMD" -m pip install --upgrade pip
    "$PYTHON_CMD" -m pip install -r "$req_file"
}

# Platform-specific optimizations
detect_platform() {
    local platform
    case "$(uname -s)" in
        Linux*)     platform="linux" ;;
        Darwin*)    platform="macos" ;;
        CYGWIN*|MINGW*|MSYS*) platform="windows" ;;
        *)          platform="unknown" ;;
    esac
    echo "$platform"
}

optimize_for_platform() {
    local platform
    platform=$(detect_platform)
    
    case "$platform" in
        linux)
            log_info "Applying Linux optimizations..."
            # Install Linux-specific dependencies if needed
            if command -v apt-get >/dev/null 2>&1; then
                # Ubuntu/Debian specific optimizations
                export DEBIAN_FRONTEND=noninteractive
            fi
            ;;
        macos)
            log_info "Applying macOS optimizations..."
            # macOS specific optimizations
            export MACOSX_DEPLOYMENT_TARGET=10.14
            ;;
        windows)
            log_info "Applying Windows optimizations..."
            # Windows specific optimizations
            ;;
        *)
            log_warn "Unknown platform: $platform"
            ;;
    esac
}

# Main build process
main() {
    log_info "Starting Kairos build process..."
    log_info "Build type: $BUILD_TYPE"
    log_info "Platform: $(detect_platform)"
    
    # Validation
    check_requirements || exit 1
    
    # Platform optimizations
    optimize_for_platform
    
    # Build process
    backup_setup_file
    
    if [[ -f "${PROJECT_ROOT}/cython.py" ]]; then
        prepare_cython_build
        build_cython_extensions
        restore_setup_files
    fi
    
    # Dependency management
    if [[ "$BUILD_TYPE" != "skip-deps" ]]; then
        update_dependencies
    fi
    
    # Package installation
    install_package
    
    # Cleanup
    if [[ "$BUILD_TYPE" != "dev" ]]; then
        run_cleanup
    fi
    
    log_info "Build completed successfully!"
    log_info "You can now run: kairos --help"
}

# Command line argument parsing (pure bash)
show_help() {
    cat << EOF
Kairos Build Script

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -h, --help          Show this help message
    -v, --verbose       Enable verbose output
    -d, --dev           Development build (editable install)
    -c, --clean         Clean build artifacts and exit
    --skip-deps         Skip dependency installation
    --python PYTHON     Python executable to use (default: python3)

ENVIRONMENT VARIABLES:
    PYTHON              Python executable path
    BUILD_TYPE          Build type: release, dev, skip-deps
    VERBOSE             Enable verbose output: true, false

EXAMPLES:
    $0                  # Standard release build
    $0 --dev            # Development build
    $0 --verbose        # Verbose output
    PYTHON=python3.11 $0 # Use specific Python version
EOF
}

# Argument parsing
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -d|--dev)
            BUILD_TYPE=dev
            shift
            ;;
        -c|--clean)
            run_cleanup
            exit 0
            ;;
        --skip-deps)
            BUILD_TYPE=skip-deps
            shift
            ;;
        --python)
            PYTHON_CMD="$2"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Run main function
main "$@"