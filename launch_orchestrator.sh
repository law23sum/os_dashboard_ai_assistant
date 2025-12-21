#!/bin/bash
################################################################################
# Launch Orchestrator - Unified Startup Script
# 
# This script provides a convenient way to launch the entire Master Orchestrator
# system with all components.
#
# Usage:
#   ./launch_orchestrator.sh [options]
#
# Options:
#   --workspace PATH    Set workspace root (default: parent of current dir)
#   --ui                Launch with web UI
#   --shell             Launch interactive shell
#   --self-heal         Enable self-healing engine
#   --debug             Enable debug mode
#   --help              Show this help message
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKSPACE_ROOT="$(dirname "$SCRIPT_DIR")"
LAUNCH_UI=false
LAUNCH_SHELL=false
ENABLE_SELF_HEAL=false
DEBUG_MODE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --workspace)
            WORKSPACE_ROOT="$2"
            shift 2
            ;;
        --ui)
            LAUNCH_UI=true
            shift
            ;;
        --shell)
            LAUNCH_SHELL=true
            shift
            ;;
        --self-heal)
            ENABLE_SELF_HEAL=true
            shift
            ;;
        --debug)
            DEBUG_MODE=true
            shift
            ;;
        --help)
            grep "^#" "$0" | grep -v "^#!/" | sed 's/^# //'
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Banner
echo -e "${BLUE}"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "    🚀 Master Orchestrator Launch System"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo -e "${NC}"

# Check dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION"

# Check for required files
if [ ! -f "$SCRIPT_DIR/os_dashboard_ai_assistant.py" ]; then
    echo -e "${RED}❌ os_dashboard_ai_assistant.py not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Master orchestrator found"

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"
echo -e "${GREEN}✓${NC} Logs directory created"

# Check workspace
if [ ! -d "$WORKSPACE_ROOT" ]; then
    echo -e "${RED}❌ Workspace directory not found: $WORKSPACE_ROOT${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Workspace: $WORKSPACE_ROOT"

# Count projects
PROJECT_COUNT=$(find "$WORKSPACE_ROOT" -maxdepth 4 -name ".git" -type d 2>/dev/null | wc -l)
echo -e "${GREEN}✓${NC} Found $PROJECT_COUNT git repositories"

echo ""
echo -e "${BLUE}Configuration:${NC}"
echo "  • Workspace: $WORKSPACE_ROOT"
echo "  • Projects: $PROJECT_COUNT"
echo "  • Web UI: $([ "$LAUNCH_UI" = true ] && echo "Yes" || echo "No")"
echo "  • Interactive Shell: $([ "$LAUNCH_SHELL" = true ] && echo "Yes" || echo "No")"
echo "  • Self-Healing: $([ "$ENABLE_SELF_HEAL" = true ] && echo "Yes" || echo "No")"
echo "  • Debug Mode: $([ "$DEBUG_MODE" = true ] && echo "Yes" || echo "No")"
echo ""

# Set environment variables
export PYTHONUNBUFFERED=1
[ "$DEBUG_MODE" = true ] && export OSDASH_DEBUG=1

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down...${NC}"
    
    # Kill all child processes
    jobs -p | xargs -r kill 2>/dev/null || true
    
    echo -e "${GREEN}✓${NC} Cleanup complete"
}

trap cleanup EXIT INT TERM

# Launch components
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}    Starting Components${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# 1. Launch Master Orchestrator
echo -e "${GREEN}🚀 Launching Master Orchestrator...${NC}"
ORCHESTRATOR_CMD="python3 $SCRIPT_DIR/os_dashboard_ai_assistant.py --root $WORKSPACE_ROOT"

if [ "$DEBUG_MODE" = true ]; then
    $ORCHESTRATOR_CMD &
else
    $ORCHESTRATOR_CMD > "$SCRIPT_DIR/logs/orchestrator_startup.log" 2>&1 &
fi

ORCHESTRATOR_PID=$!
echo -e "${GREEN}✓${NC} Orchestrator started (PID: $ORCHESTRATOR_PID)"
sleep 2

# Check if orchestrator is still running
if ! ps -p $ORCHESTRATOR_PID > /dev/null; then
    echo -e "${RED}❌ Orchestrator failed to start${NC}"
    echo -e "${YELLOW}Check logs: $SCRIPT_DIR/logs/orchestrator_startup.log${NC}"
    exit 1
fi

# 2. Launch Self-Healing Engine (if enabled)
if [ "$ENABLE_SELF_HEAL" = true ]; then
    echo ""
    echo -e "${GREEN}🛡️  Launching Self-Healing Engine...${NC}"
    
    if [ -f "$SCRIPT_DIR/scripts/self_healing_engine.py" ]; then
        python3 "$SCRIPT_DIR/scripts/self_healing_engine.py" > "$SCRIPT_DIR/logs/self_healing.log" 2>&1 &
        SELF_HEAL_PID=$!
        echo -e "${GREEN}✓${NC} Self-Healing Engine started (PID: $SELF_HEAL_PID)"
        sleep 1
    else
        echo -e "${YELLOW}⚠️  Self-healing script not found${NC}"
    fi
fi

# Wait for status report to be generated
echo ""
echo -e "${YELLOW}Waiting for initial status report...${NC}"
for i in {1..30}; do
    if [ -f "$SCRIPT_DIR/logs/status_report.json" ]; then
        echo -e "${GREEN}✓${NC} Status report generated"
        break
    fi
    sleep 1
    echo -n "."
done
echo ""

# Display initial status
if [ -f "$SCRIPT_DIR/logs/status_report.json" ]; then
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}    Initial Status${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    
    if command -v jq &> /dev/null; then
        TOTAL_PROJECTS=$(jq -r '.total_projects' "$SCRIPT_DIR/logs/status_report.json")
        ACTIVE_MONITORS=$(jq -r '.monitors.running + .monitors.healthy' "$SCRIPT_DIR/logs/status_report.json")
        TOTAL_TODOS=$(jq -r '.todos.total - .todos.completed' "$SCRIPT_DIR/logs/status_report.json")
        
        echo "  • Total Projects: $TOTAL_PROJECTS"
        echo "  • Active Monitors: $ACTIVE_MONITORS"
        echo "  • Pending TODOs: $TOTAL_TODOS"
    else
        cat "$SCRIPT_DIR/logs/status_report.json"
    fi
fi

# 3. Launch UI (if enabled)
if [ "$LAUNCH_UI" = true ]; then
    echo ""
    echo -e "${GREEN}🌐 Launching Web UI...${NC}"
    
    export OSDASH_ENABLE_ORCHESTRATOR=1
    
    if [ -f "$SCRIPT_DIR/start_ui.py" ]; then
        python3 "$SCRIPT_DIR/start_ui.py" > "$SCRIPT_DIR/logs/ui_startup.log" 2>&1 &
        UI_PID=$!
        echo -e "${GREEN}✓${NC} Web UI started (PID: $UI_PID)"
        echo -e "${BLUE}  Open: http://localhost:5173/ai/orchestrator${NC}"
        sleep 2
    else
        echo -e "${YELLOW}⚠️  UI launcher not found${NC}"
    fi
fi

# 4. Launch Interactive Shell (if enabled)
if [ "$LAUNCH_SHELL" = true ]; then
    echo ""
    echo -e "${GREEN}💻 Launching Interactive Shell...${NC}"
    
    if [ -f "$SCRIPT_DIR/scripts/interactive_shell.py" ]; then
        python3 "$SCRIPT_DIR/scripts/interactive_shell.py"
        exit 0
    else
        echo -e "${YELLOW}⚠️  Interactive shell not found${NC}"
    fi
fi

# Display running information
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}    System Running${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}✅ All components launched successfully!${NC}"
echo ""
echo "Running components:"
echo "  • Master Orchestrator (PID: $ORCHESTRATOR_PID)"
[ "$ENABLE_SELF_HEAL" = true ] && [ ! -z "$SELF_HEAL_PID" ] && echo "  • Self-Healing Engine (PID: $SELF_HEAL_PID)"
[ "$LAUNCH_UI" = true ] && [ ! -z "$UI_PID" ] && echo "  • Web UI (PID: $UI_PID)"
echo ""

echo "Available interfaces:"
echo "  • Status Report: $SCRIPT_DIR/logs/status_report.json"
[ "$LAUNCH_UI" = true ] && echo "  • Web Dashboard: http://localhost:5173/ai/orchestrator"
echo "  • API: http://localhost:8000/api/orchestrator/status"
echo "  • Interactive Shell: python3 $SCRIPT_DIR/scripts/interactive_shell.py"
echo ""

echo "Logs:"
echo "  • Master: $SCRIPT_DIR/logs/master_orchestrator.log"
[ "$ENABLE_SELF_HEAL" = true ] && echo "  • Self-Healing: $SCRIPT_DIR/logs/self_healing.log"
[ "$LAUNCH_UI" = true ] && echo "  • UI: $SCRIPT_DIR/logs/ui_startup.log"
echo ""

echo -e "${YELLOW}Press Ctrl+C to stop all components${NC}"
echo ""

# Keep running and monitor
while true; do
    # Check if orchestrator is still running
    if ! ps -p $ORCHESTRATOR_PID > /dev/null; then
        echo -e "${RED}❌ Master Orchestrator stopped unexpectedly${NC}"
        exit 1
    fi
    
    sleep 5
done
