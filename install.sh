#!/bin/bash
# Installation script for Automated Movie Cleaner

set -e

echo "=========================================="
echo "Automated Movie Cleaner - Installation"
echo "=========================================="
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check for FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "Warning: FFmpeg not found. Installing..."
    sudo apt update
    sudo apt install -y ffmpeg
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install PyTorch (CPU-only)
echo "Installing PyTorch (CPU-only)..."
pip install --upgrade pip
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "To use the tool:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run: python clean.py input.mp4 output.mp4"
echo ""

