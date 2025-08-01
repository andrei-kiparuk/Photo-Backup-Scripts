#!/bin/bash

# Setup script for Large Archive Import
# Installs dependencies and prepares environment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    error "This script is designed for macOS only."
    exit 1
fi

log "Setting up Large Archive Import environment..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    error "Homebrew is not installed. Please install Homebrew first:"
    echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

# Install system dependencies
log "Installing system dependencies..."
brew install exiftool jq bc

# Create virtual environment if it doesn't exist
VENV_DIR="./venv"
if [ ! -d "$VENV_DIR" ]; then
    log "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
log "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install Python dependencies
log "Installing Python dependencies..."
pip install -r requirements.txt

# Check if osxphotos is installed
if ! python -c "import osxphotos" &> /dev/null; then
    log "Installing osxphotos..."
    pip install osxphotos
fi

# Verify all dependencies
log "Verifying dependencies..."
missing=()

# Check system dependencies
system_deps=("exiftool" "python3" "jq" "bc")
for dep in "${system_deps[@]}"; do
    if ! command -v "$dep" &> /dev/null; then
        missing+=("$dep")
    fi
done

# Check Python packages in virtual environment
if ! python -c "import PIL" &> /dev/null 2>&1; then
    missing+=("python package: Pillow")
fi

if ! python -c "import exiftool" &> /dev/null 2>&1; then
    missing+=("python package: PyExifTool")
fi

if ! python -c "import osxphotos" &> /dev/null 2>&1; then
    missing+=("python package: osxphotos")
fi

if [ ${#missing[@]} -ne 0 ]; then
    error "Missing dependencies after installation: ${missing[*]}"
    exit 1
fi

log "All dependencies are installed and available"

# Check source directory
SOURCE_DIR="/Volumes/SlowDisk/iCloud"
if [ ! -d "$SOURCE_DIR" ]; then
    warn "Source directory does not exist: $SOURCE_DIR"
    warn "Please ensure the SlowDisk is mounted and contains the iCloud folder"
else
    log "Source directory found: $SOURCE_DIR"
fi

# Make scripts executable
log "Making scripts executable..."
chmod +x import_large_archive.sh
chmod +x date_fixer.py
chmod +x import_status.py

# Create necessary directories
log "Creating necessary directories..."
mkdir -p "/Volumes/SlowDisk/iCloud"

log "Setup completed successfully!"
echo ""
echo -e "${GREEN}Virtual environment created at: ./venv${NC}"
echo ""
echo "Next steps:"
echo "1. Ensure /Volumes/SlowDisk/iCloud contains your photo archive"
echo "2. Activate the virtual environment: source ./venv/bin/activate"
echo "3. Run: ./import_large_archive.sh"
echo "4. Monitor progress: python import_status.py status"
echo "5. View logs: python import_status.py logs"
echo ""
echo "To start fresh, run: python import_status.py reset"
echo ""
echo -e "${YELLOW}Note: Always activate the virtual environment before running Python scripts:${NC}"
echo "  source ./venv/bin/activate" 