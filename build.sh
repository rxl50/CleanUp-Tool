#!/bin/bash
# Build script for creating standalone executable (Linux/Mac)

set -e

echo "========================================"
echo "CleanUp Tool - Standalone Build Script"
echo "========================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

echo "Step 1: Installing build dependencies..."
pip3 install -r build_requirements.txt
echo

echo "Step 2: Installing application dependencies..."
pip3 install -r requirements.txt
echo

echo "Step 3: Building standalone executable..."
echo "This may take a few minutes..."
echo
python3 build_standalone.py
echo

echo "========================================"
echo "Build Complete!"
echo "========================================"
echo
echo "Your standalone executable is in the 'dist' folder:"
echo "  dist/CleanUpTool (Linux/Mac)"
echo
echo "You can now distribute this executable to other computers"
echo "without requiring Python to be installed."
echo

