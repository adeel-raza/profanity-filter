#!/bin/bash
# Quick fix to push fixed code to HF Space

echo "Adding HF Space as remote..."
git remote add hf-space https://huggingface.co/spaces/adeel-raza/video-profanity-filter 2>/dev/null || git remote set-url hf-space https://huggingface.co/spaces/adeel-raza/video-profanity-filter

echo "Pushing to HF Space..."
git push hf-space main --force

echo "Done! Space should update in a few minutes."
