---
title: Video Profanity Filter
emoji: 🎬
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: "4.44.0"
app_file: app.py
pinned: false
---

# Movie Profanity Filter

Automated AI-powered tool to remove profanity, curse words, and obscene language from videos and subtitles - making movies family-friendly.

**How it works:** The tool analyzes the audio track of any video file using AI speech-to-text transcription, detects profanity words, and automatically removes those segments from both the video file and subtitle files. Any video with profanity in the audio can be filtered and cleaned.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Whisper](https://img.shields.io/badge/Powered%20by-OpenAI%20Whisper-orange.svg)](https://github.com/openai/whisper)

## Features

- **AI-Powered Audio Transcription** - Uses OpenAI Whisper for accurate speech-to-text
- **Comprehensive Profanity Detection** - 1,132 curse words, sexual terms, and obscene language
- **Automatic Video Editing** - Cuts out profanity segments from video files using FFmpeg
- **Subtitle Cleaning** - Removes profanity words from SRT/VTT subtitle files
- **Timestamp Synchronization** - Automatically adjusts subtitles after video cuts
- **Batch Processing** - Process multiple videos at once
- **CPU & GPU Support** - Works on CPU (slower) or GPU (much faster), auto-detects available hardware
- **Efficient Processing** - No video frame analysis, only audio transcription
- **Privacy-First** - 100% local processing, no data uploads
- **Open Source** - Full transparency, MIT licensed

## What It Does

This tool automatically analyzes the **audio track** of any video file to detect and remove profanity:

1. **Transcribes audio** from your video using Whisper AI (speech-to-text)
2. **Detects profanity** in the transcribed text (1,132+ profanity words)
3. **Cuts out profanity segments** from the video file (removes audio and video)
4. **Cleans subtitles** by removing profanity words from text
5. **Synchronizes subtitles** with the edited video (adjusts timestamps)

**Result:** A clean, family-friendly version of your video with profanity removed from both the video file and subtitle files.

**Key Feature:** Any video with profanity in the audio can be filtered - the tool analyzes the audio track to identify profanity, then removes those segments from the video file and cleans the subtitles accordingly.

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/adeel-raza/profanity-filter.git
cd profanity-filter

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Clean a video (FAST - auto-detects subtitles if same name as video)
python3 clean.py movie.mp4
# Output: movie_cleaned.mp4
# Auto-detects: movie.srt (if exists in same directory)

# With explicit subtitle file (if different name)
python3 clean.py movie.mp4 --subs custom_subtitles.srt

# Process video without subtitles (SLOW - transcribes audio, takes 4-10 hours)
python3 clean.py video.mp4
# No subtitles found - will transcribe audio
```

**Default Behavior (FAST):**
- **Auto-detects subtitles**: If `movie.srt` exists in same directory as `movie.mp4`, uses it automatically
- **With subtitles**: Uses subtitle timestamps (completes in **minutes**)
- **Without subtitles**: Transcribes audio (takes **4-10 hours** for 2-hour movie)

**💡 Speed Tips:**
- **Subtitles are auto-detected** if they have the same name as the video (e.g., `movie.mp4` + `movie.srt`)
- No need to specify `--subs` if subtitle file has same name as video
- Use `--audio` flag only if you want to check audio in addition to subtitles (very slow)
- For fastest processing: Just run `python3 clean.py movie.mp4` (auto-detects subtitles)

## Detailed Usage

### Command Line Options

```bash
python3 clean.py [input_video] [output_video] [options]

Options:
  --subs SUBTITLE_FILE    Input subtitle file (SRT or VTT)
                          Default: Auto-detects if same name as video (e.g., movie.mp4 → movie.srt)
                          Only specify if subtitle file has different name
                          RECOMMENDED: Place subtitle file with same name as video for auto-detection
  --whisper-model MODEL   Whisper model size (tiny, base, small, medium, large)
                          Default: tiny (fastest, good accuracy)
                          Only used if no subtitles provided or --audio flag used
                          Note: Transcription takes 2-5x real-time on CPU (4-10 hours for 2-hour movie)
  --audio                 Also transcribe audio for profanity detection (SLOW)
                          Default: Uses subtitles if available (FAST)
                          Only use if you want to check audio in addition to subtitles
  --remove-timestamps     Manually specify timestamps to remove
                          Format: "start-end,start-end" (e.g., "10-15,30-35")
```

### Examples

#### Example 1: Basic Video Cleaning (Auto-detects subtitles)
```bash
python3 clean.py sample/fyou.mp4
# Auto-detects: sample/fyou.srt (if exists)
# Output: sample/fyou_cleaned.mp4
```

**Output:**
- ✅ Detected 22 profanity segments
- ✅ Removed 25.42 seconds of profanity
- ✅ Cleaned video: `fyou_cleaned.mp4`
- ✅ Cleaned subtitles: `fyou_cleaned.srt`

#### Example 2: Using Larger Whisper Model (Better Accuracy)
```bash
python3 clean.py movie.mp4 cleaned.mp4 --subs movie.srt --whisper-model base
```

#### Example 3: Batch Processing Multiple Videos
```bash
python3 batch_process.py input_folder/ output_folder/
```

## What Gets Filtered

The tool filters **1,132 profanity words** including:

- **F-Words**: fuck, fucking, fucked, fucker, motherfucker, and 100+ variations
- **S-Words**: shit, shitting, shitty, bullshit, horseshit, and variations
- **A-Words**: ass, asshole, asses, and 50+ compound variations
- **B-Words**: bitch, bitches, bitching, and variations
- **Sexual Terms**: sex, porn, nude, orgasm, masturbation, intercourse, etc.
- **Body Parts**: penis, vagina, breast, clit, etc.
- **Abusive Language**: whore, slut, cunt, and variations
- **Obscene Terms**: Various vulgar and offensive language
- **Adultery Terms**: cheat, cheating, adultery, affair, infidelity, etc.

**Word Matching:**
- Uses exact whole-word matching only (prevents false positives)
- Case-insensitive detection
- Handles punctuation correctly
- Fixed: No longer matches partial words (e.g., "house" won't match "whore")

## Performance

### Processing Speed

For a **2-hour movie** (129 minutes):

**On CPU (default):**
- **Audio Extraction**: ~30 seconds
- **Whisper Transcription** (tiny model): **4-10 hours** (2-5x real-time)
- **Video Cutting**: ~5-15 minutes (if profanity found)
- **Total Time**: **4-10 hours** (mostly transcription time)

**On GPU (if available):**
- **Audio Extraction**: ~30 seconds
- **Whisper Transcription** (tiny model): **1-4 hours** (0.5-2x real-time)
- **Video Cutting**: ~5-15 minutes (if profanity found)
- **Total Time**: **1-4 hours** (much faster with GPU)

**💡 Speed Tips:**
- **Fastest Option**: If you already have subtitles, use `--no-audio` flag to skip transcription (completes in minutes)
- **GPU Acceleration**: Install CUDA PyTorch for 5-10x faster transcription
- **Smaller Model**: Use `--whisper-model tiny` (fastest, still accurate)

**Note:** Whisper transcription is the bottleneck. Video cutting is fast (5-15 min regardless of video length).

### System Requirements

- **OS**: Linux, macOS, or Windows
- **Python**: 3.8 or higher
- **RAM**: 2-4 GB minimum (4+ GB recommended for long videos)
- **Storage**: ~2 GB for models and dependencies
- **CPU**: Any modern CPU (works on CPU, but slow for long videos)
- **GPU**: Optional but highly recommended for faster processing (NVIDIA GPU with CUDA support)

**Processing Time Expectations:**
- **Short videos (< 30 min)**: 1-2 hours on CPU, 15-30 min on GPU
- **Feature films (2 hours)**: 4-10 hours on CPU, 1-4 hours on GPU
- **With subtitles + `--no-audio`**: Minutes (regardless of video length)

## Project Structure

```
profanity-filter/
├── clean.py                      # Main script
├── audio_profanity_detector.py   # Whisper transcription & profanity detection
├── subtitle_processor.py         # Subtitle cleaning & timestamp adjustment
├── video_cutter.py               # FFmpeg video editing
├── timestamp_merger.py           # Merges segments for removal
├── profanity_words.py            # Shared profanity word list (1,132 words)
├── batch_process.py              # Batch processing multiple videos
├── generate_subtitles.py         # Generate SRT from video (if no subtitles)
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Advanced Usage

### Generate Subtitles (If You Don't Have Them)

```bash
python3 generate_subtitles.py video.mp4 output.srt --model tiny
```

### Process Multiple Videos

```bash
python3 batch_process.py /path/to/videos/ /path/to/output/ --whisper-model tiny
```

### Manual Timestamp Removal

```bash
python3 clean.py video.mp4 cleaned.mp4 --remove-timestamps "10-15,30-35,60-65"
```

## How It Works

The tool analyzes the **audio track** of your video to detect profanity:

1. **Audio Extraction**: Extracts audio track from video using FFmpeg
2. **Transcription**: Uses OpenAI Whisper to transcribe audio with word-level timestamps
3. **Profanity Detection**: Matches transcribed words against 1,132-word profanity list
4. **Segment Merging**: Merges nearby profanity segments (within 1 second)
5. **Video Cutting**: Uses FFmpeg to cut out profanity segments from the video file (removes both audio and video)
6. **Subtitle Processing**: Removes profanity words from subtitles and adjusts timestamps to match the cleaned video

**Important:** The tool works by analyzing the audio track - any video with profanity in the audio can be filtered, regardless of whether subtitles are provided. Subtitles are optional but will be cleaned if provided.

## Example Output

### Real Example: `sample/fyou.mp4`

**Before Cleaning:**
- Video: 3.1 minutes
- Contains: 27 profanity words detected
- Multiple instances of: fuck, fucking, asshole, shitbox, sperm

**After Cleaning:**
- Video: 2.7 minutes (25.42 seconds removed)
- 22 profanity segments cut out
- All profanity words removed from subtitles
- Clean, family-friendly version created

**Processing Output:**
```
============================================================
AUTOMATED MOVIE CLEANER - PROFANITY FILTER
============================================================
Input: sample/fyou.mp4
Output: sample/cleaned/fyou_cleaned.mp4
Subtitles: sample/fyou.srt

Step 1: Detecting profanity in audio...
------------------------------------------------------------
  ✓ Profanity search complete: 27 profanity word(s) found
  ✓ Merged into 22 segment(s)
------------------------------------------------------------
Step 1 Summary: Found 22 profanity segment(s)
    - 0.92s to 3.34s (2.42s): 'asshole'
    - 8.42s to 9.54s (1.12s): 'shitbox'
    - 14.94s to 15.86s (0.92s): 'fucking'
    - 19.38s to 20.28s (0.90s): 'fuck'
    - 23.96s to 26.98s (3.02s): 'fuck, whore'
    - 106.40s to 108.54s (2.14s): 'fuck, sperm'
    ...

Step 2: Merging segments...
  Merged into 22 segment(s) to remove

Step 3: Cutting out segments from video...
  ✓ Video cutting complete

Step 4: Processing subtitles...
  ✓ Cleaned subtitles saved

============================================================
SUCCESS!
============================================================
Cleaned video saved to: sample/cleaned/fyou_cleaned.mp4
Cleaned subtitles saved to: sample/cleaned/fyou_cleaned.srt
Removed 22 segment(s)
Total time removed: 25.42 seconds
```

**Subtitle Example:**

**Before:**
```
1
00:00:00,920 --> 00:00:03,340
You're such an asshole, you know that?

2
00:00:08,420 --> 00:00:09,540
What a shitbox this place is!

3
00:00:14,940 --> 00:00:15,860
This is fucking ridiculous!
```

**After:**
```
1
00:00:00,000 --> 00:00:00,920
You're such an , you know that?

2
00:00:00,920 --> 00:00:01,120
What a  this place is!

3
00:00:01,120 --> 00:00:02,040
This is  ridiculous!
```

*(Profanity words completely removed, timestamps adjusted)*

## Use Cases

- **Family Movie Nights** - Make any movie suitable for children
- **Content Creators** - Clean videos for broader audience
- **Educational Content** - Remove inappropriate language
- **Public Screenings** - Ensure content is appropriate
- **Personal Libraries** - Maintain family-friendly video collections

## Privacy & Security

- ✅ **100% Local Processing** - All processing happens on your machine
- ✅ **No Internet Required** - Works completely offline after installation
- ✅ **No Data Upload** - Your videos never leave your computer
- ✅ **Open Source** - Full transparency, inspect the code yourself

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Areas for Contribution

- Add more profanity words to the list
- Improve word matching accuracy (reduce false positives)
- Add support for more video formats
- Optimize processing speed
- Add more subtitle formats

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **OpenAI Whisper** - For accurate speech-to-text transcription
- **FFmpeg** - For video/audio processing
- **Python Community** - For excellent libraries

## Support

- **Issues**: [GitHub Issues](https://github.com/adeel-raza/profanity-filter/issues)
- **Discussions**: [GitHub Discussions](https://github.com/adeel-raza/profanity-filter/discussions)

## Star This Repo

If you find this tool useful, please consider giving it a star on GitHub!

---

Made for creating family-friendly content
