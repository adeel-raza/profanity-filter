---
title: Video Profanity Filter
emoji: 🎬
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: "6.0.0"
app_file: app.py
pinned: false
---

# Video Profanity Filter

Automated tool to remove profanity and curse words from videos by analyzing audio transcription and subtitle files. Perfect for creating family-friendly versions of movies and videos.

## Features

- **Audio Transcription**: Automatically transcribes video audio using OpenAI Whisper
- **Subtitle Detection**: Auto-detects existing subtitle files (SRT/VTT) for faster processing
- **Profanity Filtering**: Removes profanity segments from both video and subtitles
- **Subtitle Sync**: Automatically adjusts subtitle timestamps to match cleaned video
- **Multi-word Detection**: Detects profanity phrases like "fuck you", "ass hole"
- **YouTube Support**: Download and process videos directly from YouTube

## Installation

### Prerequisites

- Python 3.8+
- FFmpeg (for video processing)
- PyTorch (for Whisper transcription)

### Setup

```bash
# Clone the repository
git clone https://github.com/adeel-raza/profanity-filter.git
cd profanity-filter

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```bash
# With existing subtitles (FAST - completes in minutes)
python3 clean.py input_video.mp4 output_cleaned.mp4

# Auto-detect subtitles (if input_video.srt exists in same folder)
python3 clean.py input_video.mp4

# Download from YouTube, transcribe, and clean
yt-dlp -o "video.%(ext)s" "https://www.youtube.com/watch?v=VIDEO_ID"
python3 generate_subtitles.py video.mp4  # Generate SRT
python3 clean.py video.mp4 video_cleaned.mp4
```

### With Audio Transcription

If no subtitles are found, the tool automatically transcribes audio:

```bash
# Explicitly transcribe audio (SLOW - 4-10 hours for 2-hour movie on CPU)
python3 clean.py input_video.mp4 output_cleaned.mp4 --audio

# Use smaller Whisper model for faster transcription
python3 clean.py input_video.mp4 output_cleaned.mp4 --audio --whisper-model tiny
```

## How It Works

1. **Subtitle Detection**: Checks for existing SRT/VTT files (auto-detected if same name as video)
2. **Profanity Detection**: Scans subtitles for profanity words and phrases
3. **Audio Transcription** (if needed): Transcribes audio using Whisper to find profanity in spoken words
4. **Video Cutting**: Removes profanity segments from video using precise frame-accurate cutting
5. **Subtitle Processing**: Adjusts subtitle timestamps to match cleaned video and filters profanity text

## Processing Speed

- **With Subtitles**: 2-5 minutes for a 2-hour movie
- **Audio Transcription (CPU)**: 4-10 hours for a 2-hour movie
- **Audio Transcription (GPU)**: 30-60 minutes for a 2-hour movie

**Tip**: Always provide subtitle files when available for fastest processing!

## Command Line Options

```bash
python3 clean.py [input] [output] [options]

Arguments:
  input              Input video file path
  output             Output video file path (optional, defaults to input_cleaned.ext)

Options:
  --subs SUBS        Path to subtitle file (SRT or VTT)
  --audio            Force audio transcription even if subtitles exist
  --whisper-model    Whisper model size: tiny, base, small, medium, large (default: base)
```

## Examples

### Example 1: Quick Clean with Subtitles

```bash
# Video and subtitle file in same folder
python3 clean.py movie.mp4
# Output: movie_cleaned.mp4 and movie_cleaned.srt
```

### Example 2: YouTube Video

```bash
# Download video
yt-dlp -o "video.%(ext)s" "https://www.youtube.com/watch?v=XamC7-Pt8N0"

# Generate subtitles
python3 generate_subtitles.py video.mp4

# Clean video
python3 clean.py video.mp4 video_cleaned.mp4
```

### Example 3: Audio-Only Processing

```bash
# No subtitles available - transcribe audio
python3 clean.py movie.mp4 movie_cleaned.mp4 --audio --whisper-model tiny
```

## Output Files

- **Cleaned Video**: `[input]_cleaned.mp4` - Video with profanity segments removed
- **Cleaned Subtitles**: `[input]_cleaned.srt` - Subtitles with profanity filtered and timestamps adjusted

## Profanity Detection

The tool uses a comprehensive list of profanity words including:
- Curse words (fuck, shit, ass, etc.)
- Sexual terms
- Abusive language
- Multi-word phrases (fuck you, ass hole, etc.)

Profanity is detected using whole-word matching to avoid false positives.

## Technical Details

- **Video Processing**: FFmpeg with frame-accurate cutting
- **Audio Transcription**: OpenAI Whisper (word-level timestamps)
- **Subtitle Format**: SRT and VTT supported
- **Encoding**: Re-encoding for accurate timing (slower but precise)

## Troubleshooting

### "Whisper not installed"
```bash
pip install openai-whisper
```

### "FFmpeg not found"
Install FFmpeg:
- Ubuntu/Debian: `sudo apt install ffmpeg`
- macOS: `brew install ffmpeg`
- Windows: Download from https://ffmpeg.org

### Slow Processing
- Use `--whisper-model tiny` for faster transcription
- Provide subtitle files instead of transcribing audio
- Use GPU if available (automatic detection)

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or pull request.

## Support

For issues and questions, please open an issue on GitHub.
