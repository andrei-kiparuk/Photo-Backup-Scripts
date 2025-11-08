#!/bin/bash

# Run Visual Duplicate Finder
# Activates virtual environment and runs the duplicate detection script

set -euo pipefail

# Set locale for proper Unicode/international character handling
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

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

# Check if virtual environment exists
VENV_DIR="./venv"
if [ ! -d "$VENV_DIR" ]; then
    error "Virtual environment not found at $VENV_DIR"
    error "Please run: ./setup_import.sh"
    exit 1
fi

# Activate virtual environment
log "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Run the duplicate finder with all arguments
log "Starting Visual Duplicate Finder..."
python3 visual_duplicate_finder.py "$@"

log "Process complete!"
