# Quick Start Guide

## Installation (One-Time Setup)

```bash
cd movie_cleaner
./install.sh
```

Or manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

## Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Clean a video
python clean.py input.mp4 output.mp4
```

## Example

```bash
python clean.py movie.mp4 clean_movie.mp4
```

The script will:
1. Detect explicit sexual content in video
2. Detect profanity in audio
3. Merge all detections
4. Cut out all segments
5. Output clean video

## Options

- `--nsfw-threshold 0.2` - Lower = more aggressive NSFW detection
- `--sample-rate 0.3` - Lower = more accurate, slower
- `--whisper-model base` - Use larger model (tiny, base, small, medium, large)
- `--no-audio` - Skip audio profanity detection
- `--no-video` - Skip video NSFW detection

## Troubleshooting

**Import errors?**
```bash
pip install -r requirements.txt
```

**FFmpeg not found?**
```bash
sudo apt install ffmpeg
```

**Out of memory?**
- Use `--whisper-model tiny`
- Use `--sample-rate 1.0`

