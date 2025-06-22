#!/bin/bash

# PoseFit Universal Setup Script
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get Python version
get_python_version() {
    python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1,2
}

# Function to get Node.js version
get_node_version() {
    node --version 2>/dev/null | cut -d'v' -f2 | cut -d'.' -f1
}

echo "🚀 PoseFit Universal Setup Script"
echo "================================="
echo ""

# Store the root directory and navigate to it
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

print_status "Project root: $ROOT_DIR"

# Detect operating system
OS=$(detect_os)
print_platform "Detected OS: $OS"

# Check if we're in a clean state or want to force fresh setup
FORCE_FRESH=false
if [ "$1" = "--fresh" ] || [ "$1" = "-f" ]; then
    FORCE_FRESH=true
fi

# Check system requirements
print_status "Checking system requirements..."

# Check Python
if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3.12+ first."
    echo ""
    if [ "$OS" = "windows" ]; then
        echo "   Windows: Download from https://www.python.org/downloads/"
        echo "   Or use: winget install Python.Python.3.12"
    elif [ "$OS" = "macos" ]; then
        echo "   macOS: brew install python@3.12"
    else
        echo "   Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-venv python3-pip"
        echo "   Arch Linux: sudo pacman -S python python-pip"
        echo "   Fedora: sudo dnf install python3 python3-pip"
    fi
    exit 1
fi

PYTHON_VERSION=$(get_python_version)
print_success "Python version: $PYTHON_VERSION"

# Check Node.js
if ! command_exists node; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    echo ""
    if [ "$OS" = "windows" ]; then
        echo "   Windows: Download from https://nodejs.org/"
        echo "   Or use: winget install OpenJS.NodeJS"
    elif [ "$OS" = "macos" ]; then
        echo "   macOS: brew install node@18"
    else
        echo "   Using nvm (recommended):"
        echo "     curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
        echo "     nvm install 18"
        echo "     nvm use 18"
        echo "   Or install via package manager:"
        echo "     Ubuntu/Debian: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs"
        echo "     Arch Linux: sudo pacman -S nodejs npm"
    fi
    exit 1
fi

NODE_VERSION=$(get_node_version)
print_success "Node.js version: v$NODE_VERSION"

# Check npm
if ! command_exists npm; then
    print_error "npm is not installed. Please install npm."
    exit 1
fi

# Platform-specific setup
if [ "$OS" = "windows" ]; then
    print_platform "Running Windows-specific setup..."
    
    # Check if we're in WSL
    if grep -q Microsoft /proc/version 2>/dev/null; then
        print_warning "Detected WSL environment. Some Windows-specific features may not work."
    fi
fi

if [ "$FORCE_FRESH" = true ]; then
    print_warning "Force fresh setup requested. Removing existing environments..."
    rm -rf backend/venv
    rm -rf frontend/node_modules
    rm -f frontend/package-lock.json
fi

# Backend setup
echo ""
print_status "Setting up backend..."

cd backend

# Remove existing virtual environment if it exists
if [ -d "venv" ]; then
    print_warning "Removing existing virtual environment..."
    rm -rf venv
fi

# Create fresh virtual environment
print_status "Creating fresh virtual environment..."
python3 -m venv venv

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
if [ -f "requirements/development.txt" ]; then
    pip install -r requirements/development.txt
else
    print_error "requirements/development.txt not found!"
    exit 1
fi

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating environment file..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Please edit .env file with your database credentials and API keys"
    elif [ -f "env.example" ]; then
        cp env.example .env
        print_warning "Please edit .env file with your database credentials and API keys"
    else
        print_warning "No .env.example found. You may need to create .env manually."
    fi
fi

# Run migrations
print_status "Running database migrations..."
python manage.py makemigrations --verbosity=0
python manage.py migrate --verbosity=0

# Create superuser (optional)
echo ""
read -p "👤 Would you like to create a superuser? (y/n): " create_superuser
if [[ $create_superuser =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

cd ..

# Frontend setup
echo ""
print_status "Setting up frontend..."

cd frontend

# Remove existing node_modules if force fresh
if [ "$FORCE_FRESH" = true ] && [ -d "node_modules" ]; then
    print_warning "Removing existing node_modules..."
    rm -rf node_modules
    rm -f package-lock.json
fi

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
npm install

cd ..

# Make scripts executable
print_status "Setting up scripts..."
chmod +x scripts/*.sh

# Platform-specific instructions
echo ""
print_success "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit backend/.env with your database credentials"
echo "   2. Run the appropriate start script for your platform"
echo ""

if [ "$OS" = "windows" ]; then
    echo "🪟 Windows commands:"
    echo "   Start servers:     scripts\\start.bat"
    echo "   Backend only:      cd backend && venv\\Scripts\\activate && python manage.py runserver"
    echo "   Frontend only:     cd frontend && npm run dev"
    echo "   Fresh setup:       scripts\\setup.bat"
else
    echo "🐧 Linux/macOS commands:"
    echo "   Start servers:     ./scripts/start.sh"
    echo "   Backend only:      cd backend && source venv/bin/activate && python manage.py runserver"
    echo "   Frontend only:     cd frontend && npm run dev"
    echo "   Fresh setup:       ./scripts/setup_linux.sh --fresh"
fi

echo ""
echo "🌐 Access points:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   Admin:    http://localhost:8000/admin"
echo ""
echo "🛠️  Universal commands:"
echo "   Fresh setup:       ./scripts/setup_universal.sh --fresh"
echo "   Platform detect:   ./scripts/setup_universal.sh"
echo ""
print_success "Happy coding! 🚀" 