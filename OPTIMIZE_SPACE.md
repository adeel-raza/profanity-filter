# Space Optimization Guide

## Current Space Usage: 5.3GB

### Breakdown:
- **movies/**: 3.4GB (video files - expected)
- **venv/**: 2.0GB (virtual environment - can be optimized)

## Optimization Options

### 1. Remove Unused Dependencies (Save ~500MB)

These packages are installed but NOT in requirements.txt and NOT used in code:
- `transformers` (115MB) - Not used
- `opencv-python` (179MB) - Not used (was for old NSFW detection)
- `sympy` (74MB) - Not used
- `onnxruntime` (53MB) - Not used
- `yt-dlp` (25MB) - Not used

**To remove:**
```bash
source venv/bin/activate
pip uninstall transformers opencv-python opencv-python-headless sympy onnxruntime yt-dlp -y
```

### 2. Optimize PyTorch (Already Done ✓)

You're already using CPU-only PyTorch (2.9.1+cpu), which is optimal.

### 3. Move Processed Videos

After cleaning videos, you can:
- Delete original videos (keep only cleaned versions)
- Move videos to external storage
- Use symbolic links if videos are elsewhere

### 4. Clean Cache Regularly

Run the cleanup script:
```bash
./cleanup_space.sh
```

## Recommended Actions

1. **Remove unused packages** (saves ~500MB):
   ```bash
   source venv/bin/activate
   pip uninstall transformers opencv-python opencv-python-headless sympy onnxruntime yt-dlp -y
   ```

2. **Move processed videos** (saves 1.7GB if you delete originals):
   - Keep only `*_cleaned.mp4` files
   - Delete original videos after verification

3. **Total potential savings: ~2.2GB** (from 5.3GB to ~3.1GB)

