#!/bin/bash

# Activation script for PhotosBackup virtual environment
# Source this file to activate the virtual environment

if [ -d "./venv" ]; then
    echo "Activating virtual environment..."
    source ./venv/bin/activate
    echo "Virtual environment activated. Python packages are now available."
    echo "To deactivate, run: deactivate"
else
    echo "Virtual environment not found. Please run ./setup_import.sh first."
    exit 1
fi