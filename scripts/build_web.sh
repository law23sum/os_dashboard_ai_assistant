#!/bin/bash
# Build script for web deployment
# This creates a production-ready web build that can be deployed to any static hosting service

set -e

echo "🌐 Building AI OS for Web Deployment"
echo "=========================================================="

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

echo "🏗️  Building web application..."
npm run build:web

echo "✅ Web build complete!"
echo ""
echo "📂 Build output: frontend/dist/"
echo ""
echo "🚀 Deployment options:"
echo "  1. Static hosting (Vercel, Netlify, GitHub Pages):"
echo "     - Upload the frontend/dist/ folder"
echo "  2. Docker container:"
echo "     - Use the provided Dockerfile"
echo "  3. FastAPI server:"
echo "     - Run: python -m assistant_hub.api.server"
echo ""
echo "🔗 The web app will connect to your backend API"
echo "   Make sure to configure the API endpoint in production"

