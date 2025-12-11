#!/bin/bash

# CollabHub Local Development Management Script
# Usage: ./ops/startup.sh [start|stop|restart|status|setup|update]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"
PYTHON_BIN="$VENV_DIR/bin/python"
PIP_BIN="$VENV_DIR/bin/pip"
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"
MANAGE_PY="$PROJECT_ROOT/manage.py"
PID_FILE="$PROJECT_ROOT/ops/.dev_server.pid"
SETTINGS_MODULE="mysite.settings.dev"
DEFAULT_PORT=8000

# Helper functions
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        return 1
    fi
    return 0
}

# Create virtual environment
create_venv() {
    print_info "Creating virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    print_success "Virtual environment created"
}

# Activate virtual environment
activate_venv() {
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
    else
        print_error "Virtual environment not found at $VENV_DIR"
        exit 1
    fi
}

# Install/update dependencies
install_dependencies() {
    print_info "Installing/updating dependencies from requirements.txt..."
    "$PIP_BIN" install --upgrade pip
    "$PIP_BIN" install -r "$REQUIREMENTS_FILE"
    print_success "Dependencies installed/updated"
}

# Run database migrations
run_migrations() {
    print_info "Running database migrations..."
    export DJANGO_SETTINGS_MODULE=$SETTINGS_MODULE
    "$PYTHON_BIN" "$MANAGE_PY" migrate --noinput
    print_success "Migrations completed"
}

# Check if server is running
is_server_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        else
            # PID file exists but process is dead
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Setup environment (first-time or full setup)
setup() {
    print_info "Setting up CollabHub development environment..."
    
    # Check for Python 3
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8-3.10."
        exit 1
    fi
    
    # Check Python version compatibility
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    print_info "Detected Python version: $PYTHON_VERSION"
    
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
        print_error "Python $PYTHON_VERSION detected. Django 3.2 requires Python 3.8-3.10."
        print_error "Please use Python 3.10 or lower, or upgrade Django to 4.2+."
        print_info "To use Python 3.10 with pyenv:"
        print_info "  pyenv install 3.10.13"
        print_info "  pyenv local 3.10.13"
        exit 1
    fi
    
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]; then
        print_warning "Python $PYTHON_VERSION detected. Django 3.2 recommends Python 3.8+."
    fi
    
    # Create venv if it doesn't exist
    if ! check_venv; then
        create_venv
    else
        print_success "Virtual environment already exists"
    fi
    
    # Activate venv
    activate_venv
    
    # Install dependencies
    install_dependencies
    
    # Run migrations
    run_migrations
    
    print_success "Setup complete! Use './ops/startup.sh start' to start the server."
}

# Update dependencies without full setup
update() {
    print_info "Updating dependencies..."
    
    if ! check_venv; then
        print_error "Virtual environment not found. Run './ops/startup.sh setup' first."
        exit 1
    fi
    
    activate_venv
    install_dependencies
    run_migrations
    
    print_success "Dependencies updated. Restart server if it's running."
}

# Start the development server
start() {
    if is_server_running; then
        print_warning "Server is already running (PID: $(cat $PID_FILE))"
        status
        exit 0
    fi
    
    print_info "Starting CollabHub development server..."
    
    # Ensure venv exists
    if ! check_venv; then
        print_warning "Virtual environment not found. Running setup..."
        setup
    fi
    
    # Activate venv
    activate_venv
    
    # Run migrations if needed (silent check - only shows output if there are migrations)
    export DJANGO_SETTINGS_MODULE=$SETTINGS_MODULE
    "$PYTHON_BIN" "$MANAGE_PY" migrate --check > /dev/null 2>&1 || {
        print_info "Running pending migrations..."
        "$PYTHON_BIN" "$MANAGE_PY" migrate --noinput
    }
    
    # Start server in background
    export DJANGO_SETTINGS_MODULE=$SETTINGS_MODULE
    print_info "Starting Django development server on port $DEFAULT_PORT..."
    nohup "$PYTHON_BIN" "$MANAGE_PY" runserver "0.0.0.0:$DEFAULT_PORT" > "$PROJECT_ROOT/ops/dev_server.log" 2>&1 &
    
    SERVER_PID=$!
    echo $SERVER_PID > "$PID_FILE"
    
    # Wait a moment and check if server started successfully
    sleep 2
    if ps -p $SERVER_PID > /dev/null 2>&1; then
        print_success "Server started successfully (PID: $SERVER_PID)"
        print_info "Server running at: http://127.0.0.1:$DEFAULT_PORT"
        print_info "Admin interface: http://127.0.0.1:$DEFAULT_PORT/admin"
        print_info "Logs: $PROJECT_ROOT/ops/dev_server.log"
    else
        print_error "Server failed to start. Check logs at: $PROJECT_ROOT/ops/dev_server.log"
        rm -f "$PID_FILE"
        exit 1
    fi
}

# Stop the development server
stop() {
    if ! is_server_running; then
        print_warning "Server is not running"
        exit 0
    fi
    
    PID=$(cat "$PID_FILE")
    print_info "Stopping server (PID: $PID)..."
    
    kill $PID 2>/dev/null || true
    
    # Wait for process to terminate
    for i in {1..10}; do
        if ! ps -p $PID > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done
    
    # Force kill if still running
    if ps -p $PID > /dev/null 2>&1; then
        print_warning "Force killing server..."
        kill -9 $PID 2>/dev/null || true
    fi
    
    rm -f "$PID_FILE"
    print_success "Server stopped"
}

# Restart the server
restart() {
    print_info "Restarting server..."
    stop
    sleep 1
    start
}

# Show server status
status() {
    if is_server_running; then
        PID=$(cat "$PID_FILE")
        print_success "Server is running (PID: $PID)"
        print_info "Server URL: http://127.0.0.1:$DEFAULT_PORT"
        
        # Show last few log lines
        if [ -f "$PROJECT_ROOT/ops/dev_server.log" ]; then
            echo ""
            print_info "Last 5 log lines:"
            tail -n 5 "$PROJECT_ROOT/ops/dev_server.log"
        fi
    else
        print_warning "Server is not running"
    fi
}

# Show usage
usage() {
    echo "CollabHub Development Management Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  setup     - First-time setup: create venv, install dependencies, run migrations"
    echo "  start     - Start the development server (uses existing venv)"
    echo "  stop      - Stop the development server"
    echo "  restart   - Restart the development server"
    echo "  update    - Update dependencies and run migrations (without restarting)"
    echo "  status    - Show server status"
    echo ""
    echo "Examples:"
    echo "  $0 setup      # Run this first time"
    echo "  $0 start      # Start server"
    echo "  $0 update     # Update dependencies after pulling new code"
    echo "  $0 restart    # Restart after updates"
    echo "  $0 stop       # Stop server"
}

# Main command handler
case "${1:-}" in
    setup)
        setup
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    update)
        update
        ;;
    status)
        status
        ;;
    *)
        usage
        exit 0
        ;;
esac
