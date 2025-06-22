#!/bin/bash

# PoseFit Universal Start Script
# Works on both Windows (WSL/Git Bash) and Linux

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_platform() {
    echo -e "${CYAN}[PLATFORM]${NC} $1"
}

# Function to detect operating system
detect_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux";;
        Darwin*)    echo "macos";;
        CYGWIN*)    echo "windows";;
        MINGW*)     echo "windows";;
        MSYS*)      echo "windows";;
        *)          echo "unknown";;
    esac
}

echo "🚀 PoseFit Universal Start Script"
echo "================================="
echo ""

# Store the root directory
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

print_status "Project root: $ROOT_DIR"

# Detect operating system
OS=$(detect_os)
print_platform "Detected OS: $OS"

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    print_error "Virtual environment not found. Please run setup first."
    echo ""
    if [ "$OS" = "windows" ]; then
        echo "   Run: scripts\\setup.bat"
    else
        echo "   Run: ./scripts/setup_linux.sh"
    fi
    echo "   Or use universal setup: ./scripts/setup_universal.sh"
    exit 1
fi

# Check if Node.js dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    print_error "Node.js dependencies not found. Please run setup first."
    echo ""
    if [ "$OS" = "windows" ]; then
        echo "   Run: scripts\\setup.bat"
    else
        echo "   Run: ./scripts/setup_linux.sh"
    fi
    echo "   Or use universal setup: ./scripts/setup_universal.sh"
    exit 1
fi

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    print_warning "Stopping servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        print_status "Backend server stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        print_status "Frontend server stopped"
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start Django backend server
print_status "Starting Django backend server..."
cd "$ROOT_DIR/backend"

# Platform-specific virtual environment activation
if [ "$OS" = "windows" ]; then
    # Windows (Git Bash, WSL, etc.)
    source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
else
    # Linux/macOS
    source venv/bin/activate
fi

# Run Django server in background
python manage.py runserver 0.0.0.0:8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start Vue.js frontend server
print_status "Starting Vue.js frontend server..."
cd "$ROOT_DIR/frontend"

# Run Vue.js server in background
npm run dev &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 3

echo ""
print_success "Servers started successfully!"
echo ""
echo "🌐 Access points:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   Admin:    http://localhost:8000/admin"
echo ""
echo "📝 Server logs:"
echo "   Backend PID:  $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "🛑 Press Ctrl+C to stop all servers"
echo ""

# Platform-specific additional info
if [ "$OS" = "windows" ]; then
    print_platform "Windows detected - servers running in background"
    echo "   To stop servers manually:"
    echo "     taskkill /PID $BACKEND_PID /F"
    echo "     taskkill /PID $FRONTEND_PID /F"
else
    print_platform "Linux/macOS detected - servers running in background"
    echo "   To stop servers manually:"
    echo "     kill $BACKEND_PID"
    echo "     kill $FRONTEND_PID"
fi

# Wait for user to stop servers
wait 