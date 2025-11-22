# 📖 Detailed Usage Guide

## Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/adeel-raza/profanity-filter.git
cd profanity-filter
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
# Install PyTorch (CPU-only, recommended)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
pip install -r requirements.txt
```

### Step 4: Verify Installation
```bash
python clean.py --help
```

## Basic Usage

### Single Video with Subtitles
```bash
python clean.py input.mp4 output.mp4 --subs input.srt
```

### Auto-Detect Subtitles
If subtitle file has the same name as video (e.g., `movie.mp4` and `movie.srt`):
```bash
python clean.py movie.mp4 cleaned_movie.mp4
```

### Video Without Subtitles
```bash
# First generate subtitles
python generate_subtitles.py video.mp4 video.srt

# Then clean
python clean.py video.mp4 cleaned_video.mp4 --subs video.srt
```

## Advanced Options

### Use Larger Whisper Model (Better Accuracy)
```bash
python clean.py video.mp4 cleaned.mp4 --subs video.srt --whisper-model base
```

Available models (slower = more accurate):
- `tiny` - Fastest, good accuracy (default)
- `base` - Better accuracy
- `small` - Very good accuracy
- `medium` - Excellent accuracy
- `large` - Best accuracy, slowest

### Manual Timestamp Removal
```bash
python clean.py video.mp4 cleaned.mp4 --remove-timestamps "10-15,30-35,60-65"
```

### Skip Audio Detection (Subtitle Only)
```bash
python clean.py video.mp4 cleaned.mp4 --subs video.srt --no-audio
```

## Batch Processing

### Process All Videos in a Folder
```bash
python batch_process.py /path/to/videos/ /path/to/output/
```

### Process with Custom Whisper Model
```bash
python batch_process.py input/ output/ --whisper-model base
```

## Examples

### Example 1: Clean a Movie
```bash
python clean.py "The Matrix.mp4" "The Matrix Clean.mp4" --subs "The Matrix.srt"
```

### Example 2: Process Sample Video
```bash
python clean.py sample/fyou.mp4 sample/cleaned/fyou_cleaned.mp4 --subs sample/fyou.srt
```

### Example 3: Generate and Clean
```bash
# Generate subtitles first
python generate_subtitles.py movie.mp4 movie.srt

# Then clean
python clean.py movie.mp4 cleaned_movie.mp4 --subs movie.srt
```

## Troubleshooting

### FFmpeg Not Found
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Whisper Model Download Issues
Models are downloaded automatically on first use. If download fails:
- Check internet connection
- Models are cached in `~/.cache/whisper/`

### Out of Memory
- Use smaller Whisper model (`tiny` or `base`)
- Process shorter videos
- Close other applications

## Performance Tips

1. **Use `tiny` model** for fastest processing (good accuracy)
2. **Process shorter clips** first to test
3. **Close other applications** to free up RAM
4. **Use SSD storage** for faster video I/O

