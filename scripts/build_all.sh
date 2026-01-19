#!/bin/bash
# Build script for both web and desktop deployments
# This creates all deployment artifacts

set -e

SCRIPT_DIR="$(dirname "$0")"

echo "🚀 Building AI OS - All Targets"
echo "====================================================="
echo ""

# Build web version
echo "Step 1/2: Building web version..."
bash "$SCRIPT_DIR/build_web.sh"

echo ""
echo "Step 2/2: Building desktop version..."
bash "$SCRIPT_DIR/build_desktop.sh"

echo ""
echo "✨ All builds complete!"
echo ""
echo "📦 Deployment artifacts:"
echo "  Web:     frontend/dist/"
echo "  Desktop: frontend/dist-electron/"
echo ""
echo "🎯 Next steps:"
echo "  1. Test the builds locally"
echo "  2. Deploy web build to hosting service"
echo "  3. Distribute desktop installers"

