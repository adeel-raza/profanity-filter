#!/bin/bash
# Cleanup script to reduce folder size

echo "=== Movie Cleaner Space Cleanup ==="
echo ""

# 1. Remove Python cache files
echo "1. Cleaning Python cache files..."
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyo" -delete
echo "   ✓ Python cache cleaned"

# 2. Remove old NSFW detector cache (if any)
echo ""
echo "2. Checking for old NSFW detector files..."
if [ -f "__pycache__/nsfw_detector.cpython"* ] || [ -f "__pycache__/nsfw_detector_fast.cpython"* ] || [ -f "__pycache__/nsfw_detector_enhanced.cpython"* ]; then
    rm -f __pycache__/nsfw_detector*.cpython*
    echo "   ✓ Removed old NSFW detector cache"
else
    echo "   ✓ No old NSFW files found"
fi

# 3. Check venv size
echo ""
echo "3. Virtual environment size:"
du -sh venv/ 2>/dev/null || echo "   No venv found"

# 4. Check movies folder size
echo ""
echo "4. Movies folder size:"
du -sh movies/ 2>/dev/null || echo "   No movies folder"

# 5. Summary
echo ""
echo "=== Summary ==="
echo "To reduce space further:"
echo "  - Movies folder (3.4GB): Move processed videos elsewhere or delete originals after cleaning"
echo "  - venv (2.2GB): This is normal for PyTorch. Consider using CPU-only version if you don't need GPU"
echo ""
echo "Current folder size:"
du -sh . 2>/dev/null

