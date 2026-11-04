#!/bin/bash

echo "🚀 Starting OS Dashboard AI Assistant with all new features..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python 3 not found. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js not found. Please install Node.js 16 or higher.${NC}"
    exit 1
fi

# The backend refuses to start without a JWT signing secret.
if [ -z "${OSDASH_JWT_SECRET:-}" ]; then
    echo -e "${YELLOW}⚠️  OSDASH_JWT_SECRET is not set. Generate one with:${NC}"
    echo "    export OSDASH_JWT_SECRET=\"\$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')\""
    exit 1
fi

echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
python3 -m pip install -q -r requirements.txt

echo -e "${GREEN}✅ Python dependencies installed${NC}"
echo ""

echo -e "${BLUE}🗄️  Initializing databases...${NC}"
# Databases will be auto-initialized on first run
echo -e "${GREEN}✅ Databases ready${NC}"
echo ""

echo -e "${BLUE}🔧 Starting Backend API on port 8000...${NC}"
cd backend_api
python3 main.py &
BACKEND_PID=$!
cd ..

echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
echo ""

# Wait for backend to start
sleep 3

echo -e "${BLUE}🌐 Starting Frontend on port 5173...${NC}"
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}📦 Installing Node.js dependencies (first time only)...${NC}"
    npm install
fi

# Skip preflight tests by default for faster local startup and to avoid
# failures when AI auto-fix credentials are not configured.
if [ -z "${OSDASH_SKIP_PREFLIGHT_TESTS:-}" ]; then
    export OSDASH_SKIP_PREFLIGHT_TESTS=1
    echo -e "${YELLOW}⚠️  Preflight tests skipped (set OSDASH_SKIP_PREFLIGHT_TESTS=0 to enable).${NC}"
fi

npm run dev &
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 OS Dashboard AI Assistant is running!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📍 Access Points:${NC}"
echo -e "   Frontend:  ${GREEN}http://localhost:5173${NC}"
echo -e "   Backend:   ${GREEN}http://localhost:8000${NC}"
echo -e "   API Docs:  ${GREEN}http://localhost:8000/swagger${NC}"
echo -e "   Admin:     ${GREEN}http://localhost:5173/admin${NC}"
echo ""
echo -e "${BLUE}🔐 Accounts:${NC}"
echo -e "   No default accounts are created. Set OSDASH_BOOTSTRAP_ADMIN_PASSWORD"
echo -e "   (12+ chars) before first start to create an initial admin, or sign up."
echo ""
echo -e "${BLUE}🆕 New Features:${NC}"
echo -e "   ✅ JWT Authentication with Login/Signup"
echo -e "   ✅ Django-style Admin Panel (/admin)"
echo -e "   ✅ Unified Logging System"
echo -e "   ✅ Enhanced Document Viewer (hex, binary, multi-format)"
echo -e "   ✅ Version Control with Diff Comparison"
echo -e "   ✅ AI-Powered File Analysis"
echo -e "   ✅ Service Dependency Tracking"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo -e "   See ${GREEN}COMPREHENSIVE_UPDATE_README.md${NC} for details"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping services...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    # Kill any remaining processes
    pkill -f "uvicorn backend_api.main:app" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for user to stop
wait
