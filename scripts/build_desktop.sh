#!/bin/bash
# Build script for desktop application (all platforms)
# This creates native installers for Linux, Windows, and macOS

set -e

echo "🖥️  Building AI OS for Desktop"
echo "===================================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Navigate to frontend directory
cd "$(dirname "$0")/../frontend" || exit 1

echo "📦 Installing dependencies..."
npm install

# Determine platform
PLATFORM=$(uname -s)
echo "🔍 Detected platform: $PLATFORM"

case "$PLATFORM" in
    Linux*)
        echo "🐧 Building for Linux..."
        npm run build:desktop:linux
        echo "✅ Linux build complete!"
        echo "📂 Output: frontend/dist-electron/"
        echo "   - AppImage (portable)"
        echo "   - DEB package (Debian/Ubuntu)"
        echo "   - RPM package (Fedora/RHEL)"
        ;;
    Darwin*)
        echo "🍎 Building for macOS..."
        npm run build:desktop:mac
        echo "✅ macOS build complete!"
        echo "📂 Output: frontend/dist-electron/"
        echo "   - DMG installer"
        echo "   - ZIP archive"
        ;;
    MINGW*|MSYS*|CYGWIN*)
        echo "🪟 Building for Windows..."
        npm run build:desktop:windows
        echo "✅ Windows build complete!"
        echo "📂 Output: frontend/dist-electron/"
        echo "   - NSIS installer"
        echo "   - Portable executable"
        ;;
    *)
        echo "❓ Unknown platform: $PLATFORM"
        echo "Building for all platforms..."
        npm run build:desktop:linux
        npm run build:desktop:windows
        npm run build:desktop:mac
        echo "✅ All platform builds complete!"
        ;;
esac

echo ""
echo "🎉 Desktop build complete!"
echo "📦 Installers are ready for distribution"

