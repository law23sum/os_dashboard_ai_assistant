#!/usr/bin/env bash
# Build script for all platforms (Linux, Windows, macOS)
# AI OS - Unified Build System

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BUILD_DIR="$PROJECT_ROOT/dist"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/"
        exit 1
    fi
    
    local node_version=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$node_version" -lt 18 ]; then
        log_error "Node.js version 18+ required. Current version: $(node -v)"
        exit 1
    fi
    log_success "Node.js $(node -v) found"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed"
        exit 1
    fi
    log_success "npm $(npm -v) found"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    log_success "Python $(python3 --version) found"
}

# Install dependencies
install_dependencies() {
    log_info "Installing frontend dependencies..."
    cd "$FRONTEND_DIR"
    npm install
    log_success "Frontend dependencies installed"
    
    log_info "Installing Python dependencies..."
    cd "$PROJECT_ROOT"
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        log_success "Python dependencies installed"
    else
        log_warning "requirements.txt not found, skipping Python dependencies"
    fi
}

# Build web version
build_web() {
    log_info "Building web version..."
    cd "$FRONTEND_DIR"
    npm run build:web
    log_success "Web build completed → frontend/dist/"
}

# Build desktop versions
build_desktop_linux() {
    log_info "Building Linux desktop version..."
    cd "$FRONTEND_DIR"
    npm run build:desktop:linux
    log_success "Linux build completed → frontend/dist-electron/"
}

build_desktop_windows() {
    log_info "Building Windows desktop version..."
    cd "$FRONTEND_DIR"
    npm run build:desktop:windows
    log_success "Windows build completed → frontend/dist-electron/"
}

build_desktop_mac() {
    log_info "Building macOS desktop version..."
    cd "$FRONTEND_DIR"
    npm run build:desktop:mac
    log_success "macOS build completed → frontend/dist-electron/"
}

# Build all desktop platforms
build_all_desktop() {
    log_info "Building all desktop platforms..."
    cd "$FRONTEND_DIR"
    
    # Build web assets first
    npm run build:web
    
    # Build for all platforms
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_info "Detected Linux, building Linux version..."
        build_desktop_linux
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_info "Detected macOS, building macOS version..."
        build_desktop_mac
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        log_info "Detected Windows, building Windows version..."
        build_desktop_windows
    else
        log_warning "Unknown OS type: $OSTYPE, building for current platform..."
        npm run build:desktop
    fi
    
    log_success "Desktop builds completed"
}

# Package Python backend
package_python_backend() {
    log_info "Packaging Python backend..."
    cd "$PROJECT_ROOT"
    
    # Create distribution directory
    mkdir -p "$BUILD_DIR/backend"
    
    # Copy necessary files
    cp -r assistant_hub "$BUILD_DIR/backend/" 2>/dev/null || true
    cp -r assistant_hub_gui "$BUILD_DIR/backend/" 2>/dev/null || true
    cp -r assistant_core "$BUILD_DIR/backend/" 2>/dev/null || true
    cp -r ai_os "$BUILD_DIR/backend/" 2>/dev/null || true
    cp -r backend_api "$BUILD_DIR/backend/" 2>/dev/null || true
    cp requirements.txt "$BUILD_DIR/backend/" 2>/dev/null || true
    cp run.py "$BUILD_DIR/backend/" 2>/dev/null || true
    cp start_ui.py "$BUILD_DIR/backend/" 2>/dev/null || true
    
    log_success "Python backend packaged → dist/backend/"
}

# Create release archives
create_archives() {
    log_info "Creating release archives..."
    cd "$PROJECT_ROOT"
    
    local release_dir="$BUILD_DIR/releases"
    mkdir -p "$release_dir"
    
    # Archive web build
    if [ -d "$FRONTEND_DIR/dist" ]; then
        log_info "Archiving web build..."
        cd "$FRONTEND_DIR"
        tar -czf "$release_dir/os-dashboard-web-$TIMESTAMP.tar.gz" dist/
        log_success "Web archive created"
    fi
    
    # Archive desktop builds
    if [ -d "$FRONTEND_DIR/dist-electron" ]; then
        log_info "Archiving desktop builds..."
        cd "$FRONTEND_DIR"
        tar -czf "$release_dir/os-dashboard-desktop-$TIMESTAMP.tar.gz" dist-electron/
        log_success "Desktop archive created"
    fi
    
    # Archive backend
    if [ -d "$BUILD_DIR/backend" ]; then
        log_info "Archiving backend..."
        cd "$BUILD_DIR"
        tar -czf "$release_dir/os-dashboard-backend-$TIMESTAMP.tar.gz" backend/
        log_success "Backend archive created"
    fi
    
    log_success "All archives created → dist/releases/"
}

# Generate build manifest
generate_manifest() {
    log_info "Generating build manifest..."
    
    local manifest_file="$BUILD_DIR/releases/BUILD_MANIFEST_$TIMESTAMP.txt"
    
    cat > "$manifest_file" << EOF
AI OS - Build Manifest
==========================================
Build Date: $(date)
Build ID: $TIMESTAMP
Node Version: $(node -v)
npm Version: $(npm -v)
Python Version: $(python3 --version)
Platform: $(uname -s) $(uname -m)

Build Artifacts:
----------------
EOF
    
    if [ -d "$BUILD_DIR/releases" ]; then
        ls -lh "$BUILD_DIR/releases" >> "$manifest_file"
    fi
    
    log_success "Build manifest generated → $manifest_file"
}

# Main build function
main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║   AI OS - Multi-Platform Build        ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    
    local build_target="${1:-all}"
    
    check_prerequisites
    install_dependencies
    
    case "$build_target" in
        web)
            build_web
            ;;
        desktop)
            build_all_desktop
            ;;
        linux)
            build_desktop_linux
            ;;
        windows)
            build_desktop_windows
            ;;
        mac|macos)
            build_desktop_mac
            ;;
        backend)
            package_python_backend
            ;;
        all)
            build_web
            build_all_desktop
            package_python_backend
            create_archives
            generate_manifest
            ;;
        *)
            log_error "Unknown build target: $build_target"
            echo ""
            echo "Usage: $0 [target]"
            echo ""
            echo "Targets:"
            echo "  web       - Build web version only"
            echo "  desktop   - Build desktop version for current platform"
            echo "  linux     - Build Linux desktop version"
            echo "  windows   - Build Windows desktop version"
            echo "  mac       - Build macOS desktop version"
            echo "  backend   - Package Python backend"
            echo "  all       - Build everything (default)"
            echo ""
            exit 1
            ;;
    esac
    
    echo ""
    log_success "Build completed successfully! 🎉"
    echo ""
    log_info "Build artifacts:"
    echo "  - Web: $FRONTEND_DIR/dist/"
    echo "  - Desktop: $FRONTEND_DIR/dist-electron/"
    echo "  - Backend: $BUILD_DIR/backend/"
    echo "  - Archives: $BUILD_DIR/releases/"
    echo ""
}

# Run main function
main "$@"

