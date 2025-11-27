#!/bin/bash
# Simple Mac/Linux Shell Script for Non-Technical Users
# Double-click this file (or run: bash clean_video.sh) to clean your videos!

echo "========================================"
echo "  Video Profanity Filter"
echo "  FREE VidAngel Alternative"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo ""
    echo "Mac users: Install from https://www.python.org/downloads/"
    echo "Linux users: sudo apt install python3 python3-pip"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✓ Python detected"
echo ""

# Check if dependencies are installed
if ! python3 -c "import faster_whisper" &> /dev/null; then
    echo "Installing required software (one-time only)..."
    echo "This may take 2-5 minutes..."
    echo ""
    pip3 install -r requirements.txt
    echo ""
    echo "✓ Installation complete!"
    echo ""
fi

# Prompt for video file
echo "Enter the path to your video file:"
echo "(You can drag and drop the file here, then press Enter)"
read -e VIDEO_FILE

# Remove quotes if present
VIDEO_FILE="${VIDEO_FILE%\"}"
VIDEO_FILE="${VIDEO_FILE#\"}"

# Check if file exists
if [ ! -f "$VIDEO_FILE" ]; then
    echo ""
    echo "ERROR: Video file not found!"
    echo "Please make sure the file path is correct."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo ""
echo "========================================"
echo "Processing your video..."
echo "========================================"
echo ""
echo "This may take 15-45 minutes depending on:"
echo "- Video length"
echo "- Your computer speed"
echo "- Amount of profanity detected"
echo ""
echo "You can minimize this window and do other work."
echo "DO NOT close this window until processing completes!"
echo ""

# Run the cleaning script
python3 clean.py "$VIDEO_FILE"

echo ""
echo "========================================"
echo "Processing Complete!"
echo "========================================"
echo ""
echo "Your cleaned video is saved in the same folder as the original."
echo "Filename: [original_name]_cleaned.mp4"
echo ""
read -p "Press Enter to exit..."
