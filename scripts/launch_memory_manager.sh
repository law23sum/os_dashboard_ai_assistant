#!/bin/bash
# Launch script for Memory Resource Manager Daemon

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON="${PYTHON:-python3}"

# Configuration
CONFIG_FILE="${CONFIG_FILE:-$PROJECT_ROOT/config/memory_manager_config.json}"
LOG_DIR="$PROJECT_ROOT/logs"
PID_FILE="$LOG_DIR/memory_manager.pid"
DAEMON_SCRIPT="$SCRIPT_DIR/memory_resource_manager.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v "$PYTHON" &> /dev/null; then
        log_error "Python 3 not found. Please install Python 3.8+"
        exit 1
    fi
    
    if ! "$PYTHON" -c "import psutil" 2>/dev/null; then
        log_error "psutil not installed. Installing..."
        "$PYTHON" -m pip install psutil
    fi
    
    log_info "Dependencies OK"
}

create_directories() {
    log_info "Creating necessary directories..."
    mkdir -p "$LOG_DIR"
    mkdir -p "$(dirname "$CONFIG_FILE")"
    log_info "Directories created"
}

start_daemon() {
    log_info "Starting Memory Resource Manager daemon..."
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            log_warn "Daemon is already running (PID: $PID)"
            return 1
        else
            log_warn "Stale PID file found, removing..."
            rm -f "$PID_FILE"
        fi
    fi
    
    # Start daemon in background
    cd "$PROJECT_ROOT"
    nohup "$PYTHON" "$DAEMON_SCRIPT" \
        --config "$CONFIG_FILE" \
        > "$LOG_DIR/memory_manager.out" 2>&1 &
    
    DAEMON_PID=$!
    echo $DAEMON_PID > "$PID_FILE"
    
    # Wait a moment to check if it started successfully
    sleep 2
    if ps -p "$DAEMON_PID" > /dev/null 2>&1; then
        log_info "Daemon started successfully (PID: $DAEMON_PID)"
        log_info "Logs: $LOG_DIR/memory_manager.log"
        log_info "State: $LOG_DIR/memory_manager_state.json"
        return 0
    else
        log_error "Daemon failed to start. Check logs: $LOG_DIR/memory_manager.out"
        rm -f "$PID_FILE"
        return 1
    fi
}

stop_daemon() {
    log_info "Stopping Memory Resource Manager daemon..."
    
    if [ ! -f "$PID_FILE" ]; then
        log_warn "PID file not found. Daemon may not be running."
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    if ! ps -p "$PID" > /dev/null 2>&1; then
        log_warn "Daemon is not running (stale PID file)"
        rm -f "$PID_FILE"
        return 1
    fi
    
    # Try graceful shutdown first
    kill "$PID" 2>/dev/null || true
    sleep 2
    
    # Force kill if still running
    if ps -p "$PID" > /dev/null 2>&1; then
        log_warn "Graceful shutdown failed, forcing termination..."
        kill -9 "$PID" 2>/dev/null || true
        sleep 1
    fi
    
    if ! ps -p "$PID" > /dev/null 2>&1; then
        log_info "Daemon stopped successfully"
        rm -f "$PID_FILE"
        return 0
    else
        log_error "Failed to stop daemon"
        return 1
    fi
}

status_daemon() {
    if [ ! -f "$PID_FILE" ]; then
        log_info "Daemon is not running"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        log_info "Daemon is running (PID: $PID)"
        
        # Show resource usage
        if command -v ps &> /dev/null; then
            echo ""
            ps -p "$PID" -o pid,pcpu,pmem,rss,comm
        fi
        
        # Show recent log entries
        if [ -f "$LOG_DIR/memory_manager.log" ]; then
            echo ""
            log_info "Recent log entries:"
            tail -n 5 "$LOG_DIR/memory_manager.log"
        fi
        
        return 0
    else
        log_warn "PID file exists but process is not running (stale PID)"
        rm -f "$PID_FILE"
        return 1
    fi
}

restart_daemon() {
    log_info "Restarting Memory Resource Manager daemon..."
    stop_daemon
    sleep 1
    start_daemon
}

# Main
case "${1:-start}" in
    start)
        check_dependencies
        create_directories
        start_daemon
        ;;
    stop)
        stop_daemon
        ;;
    restart)
        check_dependencies
        create_directories
        restart_daemon
        ;;
    status)
        status_daemon
        ;;
    foreground)
        log_info "Starting in foreground mode..."
        check_dependencies
        create_directories
        cd "$PROJECT_ROOT"
        "$PYTHON" "$DAEMON_SCRIPT" --config "$CONFIG_FILE" --foreground
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|foreground}"
        echo ""
        echo "Commands:"
        echo "  start      - Start the daemon in background"
        echo "  stop       - Stop the daemon"
        echo "  restart    - Restart the daemon"
        echo "  status     - Show daemon status"
        echo "  foreground - Run in foreground (for debugging)"
        exit 1
        ;;
esac

exit 0


