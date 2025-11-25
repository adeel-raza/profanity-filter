---
title: Video Profanity Filter - Remove Profanity from Videos | AI-Powered Clean Video Tool
emoji: 🎬
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: "6.0.0"
app_file: app.py
pinned: false
---

# Video Profanity Filter - AI-Powered Clean Video Tool

**Remove profanity, curse words, and offensive language from videos automatically.** Create family-friendly versions of movies and videos using AI-powered speech-to-text transcription and intelligent video editing. Perfect for content creators, educators, and families.

> **📹 See it in action**: Check out our [Before/After Example](#-beforeafter-example) below showing real results from a sample video!

## 🎯 What This Tool Does

Automatically detects and removes profanity from videos by:
- **AI Transcription**: Uses OpenAI Whisper for accurate speech-to-text
- **Smart Detection**: Identifies 1,132+ profanity words and phrases
- **Precise Cutting**: Frame-accurate video editing removes only profanity segments
- **Subtitle Sync**: Automatically adjusts subtitles to match cleaned video
- **Quality Preserved**: Maintains original video quality and file size

## ✨ Key Features

- **🤖 AI-Powered Transcription**: OpenAI Whisper for accurate speech-to-text with word-level timestamps
- **⚡ Fast Processing**: 10-30 minutes for 2-hour movies with subtitles (recommended)
- **🎯 Smart Detection**: Detects 1,132+ profanity words including multi-word phrases
- **✂️ Precise Editing**: Frame-accurate video cutting removes only profanity segments
- **📝 Subtitle Support**: Auto-detects SRT/VTT files, cleans and syncs subtitles automatically
- **📺 YouTube Ready**: Download and process videos directly from YouTube
- **🎬 Quality Preserved**: Maintains original video quality and encoding settings

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

## 📊 Before/After Example

**Real results from processing a sample video:**

| Metric | Original Video | Cleaned Video |
|--------|---------------|---------------|
| **Duration** | 3.1 minutes | 2.9 minutes |
| **File Size** | 6.3 MB | 9.5 MB |
| **Profanity Segments** | 19 instances | 0 (all removed) |
| **Time Removed** | - | 13.5 seconds |
| **Processing Time** | - | ~2 minutes |
| **Subtitle Lines** | 284 | 312 (adjusted) |

**Results:**
- ✅ All 19 profanity words/phrases detected and removed
- ✅ Perfect audio-video synchronization maintained
- ✅ Subtitle timestamps automatically adjusted
- ✅ Natural flow of content preserved
- ✅ No gaps or awkward cuts in the cleaned video

**Try it yourself**: 
The sample video files are available in the `sample/` directory. To test:
```bash
# Clone the repository first
git clone https://github.com/adeel-raza/profanity-filter.git
cd profanity-filter

# Process the sample video
python3 clean.py sample/original_video.mp4 sample/original_video_cleaned.mp4 --subs sample/original_video.srt
```

**Note**: Sample video files (`*.mp4`) are large and gitignored, but subtitle files (`*.srt`) are included. You can use your own videos or download sample videos separately to test the tool.

## 🚀 Quick Start

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
# Explicitly transcribe audio (SLOW - 4-10 hours for 2-hour movie on CPU, depending on model)
python3 clean.py input_video.mp4 output_cleaned.mp4 --audio

# Use smaller Whisper model for faster transcription
python3 clean.py input_video.mp4 output_cleaned.mp4 --audio --whisper-model tiny
```

## 🔧 How It Works

The tool uses a multi-step process to ensure accurate profanity removal:

1. **📁 Subtitle Detection**: Auto-detects existing SRT/VTT files (same name as video)
2. **🔍 Profanity Detection**: Scans subtitles for 1,132+ profanity words and multi-word phrases
3. **🎤 Audio Transcription** (if needed): Uses OpenAI Whisper to transcribe audio and detect profanity in spoken words
4. **✂️ Video Cutting**: Removes profanity segments using frame-accurate FFmpeg cutting
5. **📝 Subtitle Processing**: Filters profanity text and adjusts timestamps to match cleaned video perfectly
6. **✅ Quality Matching**: Preserves original video quality and encoding settings

## ⚡ Processing Speed

### With Subtitles (Recommended - Fastest) ⚡
- **2-hour movie**: ~10-30 minutes total
  - Subtitle profanity detection: ~1-2 minutes
  - Video cutting/encoding: ~8-25 minutes (depends on number of cuts)
  - Subtitle processing: ~5-10 seconds

### Without Subtitles (Audio Transcription Required) 🐌
- **2-hour movie on CPU**:
  - Tiny model: ~4-6 hours
  - Base model: ~6-8 hours
  - Small model: ~8-10 hours
- **2-hour movie on GPU**:
  - Tiny model: ~30-60 minutes
  - Base model: ~60-90 minutes
  - Small model: ~90-120 minutes

**💡 Pro Tip**: Always provide subtitle files when available! Processing with subtitles is **20-50x faster** than audio transcription.

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

## 🛡️ Profanity Detection

The tool uses a comprehensive database of **1,132+ profanity words and phrases** including:
- **Curse words**: Common profanity and vulgar language
- **Sexual terms**: Inappropriate sexual references
- **Abusive language**: Offensive and derogatory terms
- **Multi-word phrases**: Detects phrases like "fuck you", "ass hole", etc.

**Smart Detection**: Uses whole-word matching to avoid false positives (e.g., "class" won't trigger on "classroom").

## 🔬 Technical Details

- **Video Processing**: FFmpeg with frame-accurate cutting and quality matching
- **Audio Transcription**: OpenAI Whisper with word-level timestamps for precise detection
- **Subtitle Formats**: SRT and VTT fully supported
- **Encoding**: Smart quality matching preserves original video bitrate and settings
- **AI Model**: Uses OpenAI Whisper 'tiny' model by default (fast and accurate)

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

## 🎬 Use Cases

- **Content Creators**: Create family-friendly versions of your videos for broader audiences
- **Educators**: Prepare educational content suitable for classrooms
- **Parents**: Make movies and shows safe for children to watch
- **Streaming Platforms**: Automate content moderation and filtering
- **Video Editors**: Batch process multiple videos with profanity removal

## 📄 License

MIT License - Free to use for personal and commercial projects

## 🤝 Contributing

Contributions welcome! Please open an issue or pull request on GitHub.

## 💬 Support

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check the `USAGE.md` file for detailed guides
- **Examples**: See the `sample/` directory for before/after examples

---

**Made with ❤️ for creating family-friendly content**
