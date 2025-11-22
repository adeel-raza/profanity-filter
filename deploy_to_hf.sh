#!/bin/bash
# Script to help deploy to Hugging Face Spaces

echo "=========================================="
echo "Movie Profanity Filter - HF Spaces Deploy"
echo "=========================================="
echo ""
echo "This script will help you deploy to Hugging Face Spaces"
echo ""
echo "STEP 1: Create Hugging Face Account (if needed)"
echo "  Go to: https://huggingface.co/join"
echo ""
echo "STEP 2: Create a new Space"
echo "  Go to: https://huggingface.co/spaces"
echo "  Click: 'Create new Space'"
echo "  Name: video-profanity-filter"
echo "  SDK: Gradio"
echo "  Hardware: CPU basic"
echo ""
echo "STEP 3: Upload these files to your Space:"
echo ""

files=(
    "app.py"
    "gradio_app.py"
    "clean.py"
    "audio_profanity_detector.py"
    "subtitle_processor.py"
    "video_cutter.py"
    "timestamp_merger.py"
    "profanity_words.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (MISSING!)"
    fi
done

echo ""
echo "STEP 4: Rename requirements_hf.txt to requirements.txt in the Space"
echo ""
echo "STEP 5: Wait for deployment (5-10 minutes)"
echo ""
echo "Your app will be live at:"
echo "  https://huggingface.co/spaces/YOUR_USERNAME/video-profanity-filter"
echo ""
echo "=========================================="
echo "Files are ready in this directory!"
echo "=========================================="
