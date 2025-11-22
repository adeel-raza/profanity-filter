#!/bin/bash
# Clean a single movie with auto-detected subtitles and verbose output
# Usage: ./clean_movie.sh <video_file>

if [ -z "$1" ]; then
    echo "Usage: $0 <video_file>"
    echo "Example: $0 movies/Code_3.mkv"
    exit 1
fi

# Change to script directory first
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Handle both absolute and relative paths
if [[ "$1" == /* ]]; then
    # Absolute path
    VIDEO_FILE="$1"
else
    # Relative path - make it relative to script directory
    VIDEO_FILE="$SCRIPT_DIR/$1"
fi

# Check if file exists
if [ ! -f "$VIDEO_FILE" ]; then
    echo "Error: Input file not found: $VIDEO_FILE"
    echo "Current directory: $(pwd)"
    exit 1
fi

VIDEO_DIR=$(dirname "$VIDEO_FILE")
VIDEO_NAME=$(basename "$VIDEO_FILE" | sed 's/\.[^.]*$//')
OUTPUT_DIR="${VIDEO_DIR}/cleaned"
OUTPUT_FILE="${OUTPUT_DIR}/${VIDEO_NAME}_cleaned.${VIDEO_FILE##*.}"

# Auto-detect subtitle file
SUBTITLE_FILE="${VIDEO_DIR}/${VIDEO_NAME}.srt"
if [ ! -f "$SUBTITLE_FILE" ]; then
    # Try .en.srt pattern
    SUBTITLE_FILE="${VIDEO_DIR}/${VIDEO_NAME}.en.srt"
    if [ ! -f "$SUBTITLE_FILE" ]; then
        echo "Warning: Subtitle file not found, processing without subtitles"
        SUBTITLE_FILE=""
    fi
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Activate virtual environment
source venv/bin/activate

# Build command array (properly handles spaces in paths)
# Use absolute paths to avoid issues
VIDEO_FILE_ABS=$(realpath "$VIDEO_FILE" 2>/dev/null || echo "$VIDEO_FILE")
OUTPUT_FILE_ABS=$(realpath "$OUTPUT_FILE" 2>/dev/null || echo "$OUTPUT_FILE")

CMD_ARGS=(
    "clean.py"
    "$VIDEO_FILE_ABS"
    "$OUTPUT_FILE_ABS"
    "--fast"
    "--nsfw-threshold" "0.3"
    "--sample-rate" "0.5"
)

if [ -n "$SUBTITLE_FILE" ] && [ -f "$SUBTITLE_FILE" ]; then
    SUBTITLE_FILE_ABS=$(realpath "$SUBTITLE_FILE" 2>/dev/null || echo "$SUBTITLE_FILE")
    CMD_ARGS+=("--subs" "$SUBTITLE_FILE_ABS")
fi

# Run with unbuffered output for real-time verbose display
export PYTHONUNBUFFERED=1
python "${CMD_ARGS[@]}"

