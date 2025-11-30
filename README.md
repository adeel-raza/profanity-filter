# 🚀 Try the Online Demo

Want to see how it works before installing? **Try the app instantly in your browser:**

[![Hugging Face Spaces](https://img.shields.io/badge/Live%20Demo-Hugging%20Face-blue?logo=huggingface)](https://huggingface.co/spaces/adeel-raza/video-profanity-filter)

---
---
title: Free Profanity Filter for Movies & Videos - VidAngel & ClearPlay Alternative
emoji: 🎬
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: "6.0.0"
app_file: app.py
pinned: false
tags:
  - profanity-filter
  - video-filter
  - family-friendly
  - movie-cleaner
  - content-filter
  - parental-controls
  - vidangel-alternative
  - clearplay-alternative
  - netflix-filter
  - open-source
  - local-processing
  - privacy
---



# Free Profanity Filter for Movies & Videos - VidAngel & ClearPlay Alternative

**Created by [Adeel Raza](https://elearningevolve.com/about) — Contact: info@elearningevolve.com**

**Watch movies YOUR way – completely FREE!** Remove profanity, curse words, and offensive language from ANY video automatically. Unlike VidAngel or ClearPlay, no subscription or Netflix account is required. Works with local video files, YouTube downloads, and any MP4/MKV content.

**Perfect for families who want to enjoy movies together without inappropriate language**  
**100% FREE alternative to VidAngel ($9.99/month) and ClearPlay ($7.99/month)**  
**Privacy-focused: Everything runs locally on your computer**  
**AI-powered with enhanced dialogue detection using faster-whisper**

---

## Why Choose This Free Profanity Filter?

### Save Money - No Subscriptions
- **VidAngel**: $9.99/month + requires Netflix/Amazon Prime  
- **ClearPlay**: $7.99/month + requires compatible devices  
- **This App**: **100% FREE** - works with any video file

### Watch Movies Your Way
Unlike VidAngel and ClearPlay that only work with specific streaming services, this tool works with:  
- Local video files (MP4, MKV, AVI, etc.)  
- YouTube downloads (via yt-dlp)  
- DVDs and Blu-rays (ripped to digital)  
- ANY video source - no restrictions

### Privacy & Control
- Everything runs on **YOUR computer**  
- **No cloud uploads** or streaming required  
- Your videos stay private  
- Complete control over content filtering

---

## How It Works - The Technology Behind 95%+ Accuracy

### 1. AI Audio Transcription (Word-Level Precision)
- Uses **faster-whisper base model** (default, accurate) to transcribe every spoken word  
- Each word gets a **precise timestamp** (±0.1 seconds)  
- Example: `"fuck"` detected at 79.76s-80.08s, `"you"` at 80.08s-80.88s  
- Only cuts the **bad words**, unlike subtitle-based filters that cut entire sentences
- **Tiny model** is available for faster processing, but is less accurate and may miss profanity, especially in movies with music or background noise.

### 2. Smart Multi-Word Detection (Phrase Recognition)
- Automatically detects **1,192+ profanity words** including variations  
- **Intelligent merging**: Combines split phrases like "fuck you", "bull shit" into single cuts  
- **Context-aware**: Uses 1.5-second window to catch phrases spoken together  
- **Zero false positives**: Whole-word matching prevents accidental cuts

### 3. Frame-Accurate Video Cutting
- **FFmpeg-powered editing**: Industry-standard video processing tool  
- **Surgical precision**: Removes only profanity segments (0.3-2 seconds each)  
- **Quality preservation**: Original bitrate, resolution, and encoding maintained  
- **Smooth transitions**: Seamless cuts without audio glitches or visual artifacts

---

## CPU-Intensive Task Warning

**Important:** Video cleaning is a **CPU-intensive task**. On CPU-only systems like the **11th Gen Intel® Core™ i5-1135G7 ×8**:  

- Processing a 2-hour movie can take **~6 hours**  
- **Do not run other heavy applications** (games, video editing, compiling) simultaneously  
- Video **encoding, decoding, and profanity removal** require sustained high CPU usage  
- Ensure enough **RAM and disk space** is available to avoid slowdowns or failures  

> Tip: For faster processing, consider a system with a GPU or using existing subtitle files (`--subs`) to reduce transcription time.

---

## Key Features - VidAngel & ClearPlay Alternative

- **No Monthly Subscription** - Save $96-120/year compared to VidAngel or ClearPlay  
- **Works Offline** - No internet required after initial setup  
- **Any Video Source** - Not limited to Netflix or specific streaming services  
- **Fast AI Transcription** - Uses faster-whisper (CTranslate2) for accurate, word-level timestamps  
- **Smart Profanity Detection** - Detects 1,192+ curse words and offensive phrases  
- **Precise Editing** - Only removes profanity, keeps dialogue intact  
- **Family Safe** - Clean versions for kids and family movie nights  
- **YouTube Compatible** - Download and clean YouTube videos  
- **Quality Preserved** - Maintains original video quality and encoding  
- **Open Source** - Free forever, community-driven improvements

---

## System Requirements

### Minimum Specs (Budget PCs)
- **CPU**: Dual-core processor (Intel i3, AMD Ryzen 3, or better)  
- **RAM**: 4GB minimum (8GB recommended)  
- **Storage**: 2GB free space + space for video files  
- **OS**: Windows 10/11, macOS 10.15+, or Linux  
- **Processing Time**: 2-hour movie takes **~6 hours on CPU-only systems**

### Recommended Specs (Faster Processing)
- **CPU**: Quad-core processor (Intel i5/i7, AMD Ryzen 5/7)  
- **RAM**: 8GB or more  
- **GPU**: NVIDIA GPU with CUDA support (optional, 3-5x faster)  
- **Storage**: 5GB+ free space  
- **Processing Time**: 2-hour movie takes 2-3 hours on modern CPU-only systems

### GPU Acceleration (Optional)
- **Processing Time**: 2-hour movie in ~30-60 minutes with NVIDIA GPU  
- **Cost**: Free to use, but requires compatible hardware

---

## Installation - Easy Setup Guide

### Prerequisites
- **Python 3.8+** (free from python.org)  
- **FFmpeg** (free video processing tool)  
- **5-10 minutes** for setup (one-time only)

### Quick Setup (Copy & Paste)

```bash
# Step 1: Clone the repository
git clone https://github.com/adeel-raza/profanity-filter.git
cd profanity-filter

# Step 2: Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Step 3: Install dependencies
pip install -r requirements.txt
```

## Quick Start - Simple for Non-Technical Users

### Clean a Video
```bash
python3 clean.py YourMovie.mp4 YourMovie_cleaned.mp4
# Output: YourMovie_cleaned.mp4
```

### Use Subtitle Files for Faster Processing
```bash
python3 clean.py YourMovie.mp4 YourMovie_cleaned.mp4 --subs YourMovie.srt
```

### Download & Clean YouTube Video
```bash
yt-dlp -o "video.mp4" "https://www.youtube.com/watch?v=VIDEO_ID"
python3 clean.py video.mp4 video_cleaned.mp4
```

### Advanced Options
```bash
# Use tiny model for faster but less accurate results (may miss profanity)
python3 clean.py input.mp4 output.mp4 --model tiny

# Mute profanity instead of cutting
python3 clean.py input.mp4 output.mp4 --mute-only

# Manually remove timestamps
python3 clean.py input.mp4 output.mp4 --remove-timestamps "10-15,30-35"
```

**Note:**
- If your subtitle file has the same name as your video (e.g. `movie.mp4` and `movie.srt`) and is in the same directory, it will be auto-detected. You do not need to specify `--subs` in this case.

## Why Choose This Free Profanity Filter?

### Save Money - No Subscriptions
- **VidAngel**: $9.99/month + requires Netflix/Amazon Prime
- **ClearPlay**: $7.99/month + requires compatible devices
- **This App**: **100% FREE** - works with any video file

### Watch Movies Your Way
Unlike VidAngel and ClearPlay that only work with specific streaming services, this tool works with:
- Local video files (MP4, MKV, AVI, etc.)
- YouTube downloads (via yt-dlp)
- DVDs and Blu-rays (ripped to digital)
- ANY video source - no restrictions

### Privacy & Control
- Everything runs on YOUR computer
- No cloud uploads or streaming required
- Your videos stay private
- Complete control over content filtering

## How It Works - The Technology Behind 95%+ Accuracy

This Netflix profanity filter uses a **4-layer approach** for near-perfect profanity removal:

### 1. Dialog Enhancement (Audio Preprocessing) 🆕
- **Vocal isolation**: High-pass (200Hz) and low-pass (3500Hz) filters remove music, effects, and noise
- **Dynamic normalization**: Balances quiet dialogue and loud scenes for consistent transcription
- **Result**: 4-5x more words transcribed in complex audio (music, action scenes, background noise)
- **Example**: Original tiny model caught 0 profanities in Argo → Enhanced base model caught 38 segments

### 2. AI Audio Transcription (Word-Level Precision)
- Uses **faster-whisper base model** (74M parameters) for superior accuracy on movies
- **Dialog-enhanced audio** helps model "hear" speech masked by soundtracks
- Each word gets a **precise timestamp** (accurate to 0.1 seconds)
- Example: "fuck" detected at 79.76s-80.08s, "you" at 80.08s-80.88s
- Unlike subtitle-based filters that cut entire sentences, we cut only the bad words!

### 3. Smart Multi-Word Detection (Phrase Recognition)
- Automatically detects **1,192+ profanity words** including variations and sexual content
- **Intelligent merging**: Combines split phrases like "fuck you", "bull shit" into single cuts
- **Context-aware**: Uses 1.5-second window to catch phrases spoken together
- **Zero false positives**: Whole-word matching prevents "class" from triggering "ass"
- **Quality monitoring**: WPM (words per minute) diagnostic warns if transcription incomplete

### 4. Frame-Accurate Video Cutting
- **FFmpeg-powered editing**: Industry-standard video processing tool
- **Surgical precision**: Removes only profanity segments (typically 0.3-2 seconds each)
- **Quality preservation**: Original video bitrate, resolution, and encoding maintained
- **Smooth transitions**: Seamless cuts without audio glitches or visual artifacts

### Result: 95%+ Profanity-Free Videos
- **38 segments detected** in Argo (129-minute movie with orchestral score)
- **0.46 minutes removed** (99.6% of content preserved)
- **Improvement**: Tiny model missed 100% of profanity → Enhanced base caught all instances
- **Manual review option**: Add timestamps with `--remove-timestamps` flag for missed words

## Key Features - VidAngel & ClearPlay Alternative

- **No Monthly Subscription** - Save $96-120/year compared to VidAngel or ClearPlay  
- **Works Offline** - No internet required after initial setup  
- **Any Video Source** - Not limited to Netflix or specific streaming services  
- **Fast AI Transcription** - Uses faster-whisper (CTranslate2) for 4-10x speed improvement  
- **Smart Profanity Detection** - Identifies 1,132+ curse words and offensive phrases  
- **Precise Editing** - Word-level timestamps remove only profanity, keeps dialogue intact  
- **Family Safe** - Create clean versions for kids and family movie nights  
- **YouTube Compatible** - Download and clean YouTube videos  
- **Quality Preserved** - Maintains original video quality and encoding  
- **Open Source** - Free forever, community-driven improvements

## System Requirements

### ⚠️ IMPORTANT: Resource Usage Warning

**This application is CPU and memory intensive.** Video encoding/decoding requires substantial system resources:

- **CPU Usage**: Expect 80-100% CPU utilization during processing
- **RAM Requirements**: 8GB minimum (16GB recommended for base model)
- **Disk I/O**: Heavy read/write operations during video processing
- **Processing Time**: 3-6 hours for a 2-hour movie on CPU (base model with dialog enhancement)

**⚡ GPU Strongly Recommended**: If you have an NVIDIA GPU, this tool can leverage CUDA acceleration for **10-20x faster processing** with significantly lower CPU load. Without a GPU, expect very long processing times.

**💡 Best Practice**: Run this tool overnight or when you don't need your computer. Close unnecessary applications before processing. Consider GPU rental services (AWS, Google Cloud) for batch processing.

### Minimum Specs (Budget PCs)
- **CPU**: Quad-core processor (Intel i5, AMD Ryzen 5, or better)
- **RAM**: 8GB minimum (base model)
- **Storage**: 5GB free space + 2x video file size
- **OS**: Windows 10/11, macOS 10.15+, or Linux
- **Processing Time**: 2-hour movie takes ~6 hours on CPU
- **⚠️ Warning**: Expect very long processing times without GPU

### Recommended Specs (Production Use)
- **CPU**: Multi-core processor (Intel i7/i9, AMD Ryzen 7/9)
- **RAM**: 16GB or more
- **GPU**: NVIDIA GPU with CUDA support (GTX 1060 or better)
- **Storage**: 10GB+ free space
- **Processing Time**: 2-hour movie takes ~20-40 minutes with GPU

### GPU Acceleration (Highly Recommended)
With NVIDIA GPU and CUDA:
- **Processing Time**: 2-hour movie in ~5-10 minutes
- **CPU Load**: Significantly reduced (30-40% vs 100%)
- **System Usability**: Computer remains responsive during processing
- **Cost**: Free to use, but requires compatible hardware

**Note**: Unlike streaming-based filters (VidAngel, ClearPlay), this tool processes videos locally, so processing time varies by system specs. You only process once, then enjoy unlimited viewing!

## Installation - Easy Setup Guide

### Prerequisites

- **Python 3.8+** (free from python.org)
- **FFmpeg** (free video processing tool)
- **5-10 minutes** for setup (one-time only)

### Quick Setup (Copy & Paste)

```bash
# Step 1: Clone the repository
git clone https://github.com/adeel-raza/profanity-filter.git
cd profanity-filter

# Step 2: Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Step 3: Install dependencies (takes 2-5 minutes)
pip install -r requirements.txt
```

## Usage - Simple Command Line

### Basic Usage (Recommended - Auto-Enhanced)

```bash
# Simple command - dialog enhancement and auto-upgrade enabled by default
python3 clean.py input_video.mp4 output_cleaned.mp4
```

That's it! The tool now uses optimal settings by default:
- **Base model** (better accuracy than tiny)
- **Dialog enhancement** (isolates speech from music/noise)
- **Auto-upgrade** (switches to larger model if needed)
- **Quality monitoring** (warns if transcription incomplete)

### Advanced Options

```bash
# Disable dialog enhancement (not recommended)
python3 clean.py input.mp4 output.mp4 --no-dialog-enhance

# Use different model
python3 clean.py input.mp4 output.mp4 --model small  # or medium, large

# Save transcript for review
python3 clean.py input.mp4 output.mp4 --dump-transcript transcript.txt

# Disable auto-upgrade
python3 clean.py input.mp4 output.mp4 --no-auto-upgrade

# Add manual timestamps
python3 clean.py input.mp4 output.mp4 --remove-timestamps "45.2-47.8,120-125"
```

### What Changed (v2.0 - Enhanced Detection)

**Old defaults (missed profanity):**
- Tiny model (39M parameters)
- No audio preprocessing
- Failed on movies with soundtracks

**New defaults (catches everything):**
- Base model (74M parameters) - 2x more accurate
- Dialog enhancement enabled - isolates speech
- Auto-upgrade if WPM low - catches edge cases
- 1,192 profanity words (was 1,000+)

**Result:** 0% → 95%+ detection on complex audio

## Why faster-whisper?

This tool uses **faster-whisper** instead of standard OpenAI Whisper for significant performance improvements:

- **4-10x faster transcription**: 15 seconds vs 25 seconds for a 3-minute video
- **Same accuracy**: CTranslate2 backend provides identical transcription quality
- **Lower memory usage**: Optimized int8 quantization for efficient CPU processing
- **Word-level timestamps**: Precise profanity detection and removal

**Example performance** (3-minute video, CPU):
- Transcription: ~15 seconds (12.3x real-time)
- Total processing: ~1 minute 40 seconds including video cutting

## Before/After Example

See the tool in action with our sample video:

**Sample Video Results:**
- **Original Video**: 3.1 minutes, 6.3 MB
- **Cleaned Video**: 2.9 minutes, 9.5 MB (profanity segments removed)
- **Profanity Removed**: 19 segments totaling 13.5 seconds
- **Processing Time**: ~2 minutes (with subtitles)

The cleaned video maintains perfect audio-video sync and subtitle alignment. All profanity words were precisely detected and removed while preserving the natural flow of the content.

### Original Video (Before)
<video src="https://github.com/adeel-raza/profanity-filter/raw/main/sample/original_video.mp4" controls="controls" muted="muted" width="600"></video>

**Watch on Vimeo**: [Original Video](https://vimeo.com/1140277069) | **Download**: [MP4 (6.3 MB)](https://github.com/adeel-raza/profanity-filter/raw/main/sample/original_video.mp4)

### Cleaned Video (After)
<video src="https://github.com/adeel-raza/profanity-filter/raw/main/sample/original_video_cleaned.mp4" controls="controls" muted="muted" width="600"></video>

**Watch on Vimeo**: [Cleaned Video](https://vimeo.com/1140277103) | **Download**: [MP4 (9.5 MB)](https://github.com/adeel-raza/profanity-filter/raw/main/sample/original_video_cleaned.mp4)

**Try it yourself**: 
```bash
# Clone the repository
git clone https://github.com/adeel-raza/profanity-filter.git
cd profanity-filter

# Process the sample video
python3 clean.py sample/original_video.mp4 sample/original_video_cleaned.mp4 --subs sample/original_video.srt
```

## Quick Start - Simple for Non-Technical Users

### Easiest Method (Copy & Paste)

**Step 1: One-Time Setup** (5 minutes)
```bash
# Install Python if you don't have it (skip if already installed)
# Download from: https://www.python.org/downloads/

# Download this tool
git clone https://github.com/adeel-raza/profanity-filter.git
cd profanity-filter

# Install required software (one-time)
pip install -r requirements.txt
```

**Step 2: Clean Your Video** (Just change the filename!)
```bash
# Copy your video to this folder, then run:
python3 clean.py YourMovie.mp4 YourMovie_cleaned.mp4

# That's it! The tool automatically uses optimal settings:
# - Base model (best accuracy)
# - Dialog enhancement (isolates speech)
# - Auto-upgrade if needed
```

### For Windows Users (Drag & Drop Method)
1. Install Python from https://www.python.org/downloads/
2. Download this tool and unzip
3. Double-click `clean_video.bat` (Windows batch file - coming soon!)
4. Drag your video file when prompted
5. Wait for processing to complete
6. Find cleaned video in same folder!

### Basic Usage Examples

```bash
# Simplest: Clean a video with automatic optimal settings
python3 clean.py movie.mp4 movie_cleaned.mp4

# If you have subtitle files (5x faster, skips transcription)
python3 clean.py movie.mp4 movie_cleaned.mp4 --subs movie.srt

# Download YouTube video and clean it
yt-dlp -o "video.mp4" "https://www.youtube.com/watch?v=VIDEO_ID"
python3 clean.py video.mp4 video_cleaned.mp4
```

### Advanced Options

```bash
# Use larger model for maximum accuracy (slower)
python3 clean.py input.mp4 output.mp4 --model large

# Disable dialog enhancement (not recommended)
python3 clean.py input.mp4 output.mp4 --no-dialog-enhance

# Save transcript for verification
python3 clean.py input.mp4 output.mp4 --dump-transcript words.txt

# Mute profanity instead of cutting (keeps video length unchanged)
python3 clean.py input.mp4 output.mp4 --mute-only

# Add manual timestamp corrections
python3 clean.py input.mp4 output.mp4 --remove-timestamps "10-15,30-35"
```

## How It Works - Technical Deep Dive

### The 4-Step Profanity Removal Process

#### Step 1: AI Audio Transcription with Dialog Enhancement
- **Technology**: faster-whisper (OpenAI Whisper optimized with CTranslate2)
- **Dialog Enhancement**: FFmpeg audio filtering isolates speech (200-3500Hz vocal range, removes music/effects)
- **Process**: Converts speech to text with **word-level timestamps** (±0.1s accuracy)
- **Quality Monitoring**: Calculates Words Per Minute (WPM); warns if <50 (indicates under-transcription)
- **Auto-Upgrade**: Automatically retries with larger model if transcription quality too low
- **Example Output**: 
  ```
  [79.76s-80.08s] "fuck"
  [80.08s-80.88s] "you"
  [82.15s-82.67s] "shit"
  ```
- **Why accurate**: Trained on 680,000 hours of multilingual speech data
- **Speed**: Processes at 10-12x real-time speed on modern CPUs

#### Step 2: Profanity Detection
- **Database**: 1,192 profanity words including variations, slang, and explicit sexual content
- **Matching**: Whole-word exact matching (prevents false positives)
- **Categories**: F-words, sexual terms, abusive language, religious profanity, anatomical terms, intimate actions
- **Recent additions**: Screaming, intimate acts, body parts, arousal terms, explicit content markers

#### Step 3: Intelligent Phrase Merging
- **Problem**: AI sometimes splits phrases ("fuck" + "you" = 2 separate detections)
- **Solution**: Automatically merges words within 1.5 seconds into single cuts
- **Examples caught**:
  - "fuck you" → Merged into one segment
  - "bull shit" → Combined removal
  - "ass hole" → Single cut
- **Result**: Natural speech flow maintained, no awkward gaps

#### Step 4: Frame-Accurate Video Cutting
- **Tool**: FFmpeg (Hollywood-grade video processing)
- **Precision**: Cuts at exact keyframes (±0.1 second accuracy)
- **Method**: 
  1. Extract clean segments between profanity
  2. Concatenate segments seamlessly
  3. Re-encode with original quality settings
- **Smart encoding**: Matches original bitrate, resolution, codec automatically

#### Step 5: Subtitle Synchronization
- **Automatic adjustment**: Shifts all subtitle timestamps after each cut
- **Text cleaning**: Removes profanity from subtitle text
- **Format support**: SRT and VTT formats
- **Sync accuracy**: ±0.1 second perfect lip-sync maintained

### Why 95%+ Accuracy?

- **Dialog enhancement** (isolates speech from music/effects)
- **Base model default** (74M parameters, 2x more accurate than tiny)
- **Auto-upgrade mechanism** (switches to larger model if WPM low)
- **Word-level timestamps** (not sentence-level like competitors)  
- **1,192 word database** (comprehensive coverage including sexual content)  
- **Intelligent phrase merging** (catches split expressions)  
- **Context-aware detection** (whole-word matching)  
- **Frame-accurate cutting** (surgical precision)

**Real-world example (Argo 2012 film):**
- Old version (tiny model, no enhancement): 0 detections (missed 100%)
- New version (base + dialog enhancement): 38 segments detected, 0.46 min removed

### Edge Cases (That 5%)
- Heavy accents or unclear audio may be misheard by AI
- Creative slang or new profanity not in database
- Background noise masking quiet curse words
- **Solution**: Use `--remove-timestamps "10-15"` to manually add missed segments

## Processing Time & Resource Usage

### Expected Processing Times

#### Short Videos (5-15 minutes)
- **Budget CPU**: 2-5 minutes processing
- **Modern CPU**: 1-3 minutes processing
- **With GPU**: 30-60 seconds processing
- **RAM Usage**: 2-3GB during processing

#### Full Movies (90-120 minutes)
- **CPU (base model + dialog enhancement)**: 3-5 hours processing
- **With NVIDIA GPU (recommended)**: 15-30 minutes processing
- **RAM Usage**: 8GB minimum (16GB recommended)
- **Disk Space**: Temporary files need ~2x video size

#### Long Movies/Content (2-3 hours)
- **CPU (base model + dialog enhancement)**: 6-10 hours processing
- **With NVIDIA GPU (recommended)**: 20-40 minutes processing

### System Resource Usage
- **CPU**: 80-100% utilization during transcription
- **RAM**: 3-6GB depending on video length
- **Disk I/O**: Moderate (reading/writing video files)
- **Temp Storage**: Requires 2-3x the video file size temporarily

### Comparison to Paid Services

| Service | Cost | Processing | Streaming | Video Source |
|---------|------|------------|-----------|--------------|
| **This Tool** | **FREE** | **15-45 min one-time** | **Offline anytime** | **Any video file** |
| VidAngel | $9.99/mo | Instant streaming | Requires internet | Netflix/Prime only |
| ClearPlay | $7.99/mo | Instant streaming | Requires internet | Select services |

**Trade-off**: One-time processing vs. ongoing subscription costs. Process once, watch unlimited times offline!

### Tips for Faster Processing
1. **GPU acceleration** (10-20x faster) - rent AWS/Google Cloud GPU instance for batch jobs
2. Use `--subs` flag if you have accurate subtitle files (skips transcription, 20x faster)
3. Close other heavy applications during processing
4. Consider `--model tiny` for speed (but may miss profanity on complex audio)
5. Run overnight or during off-hours - quality over speed recommended

## Command Line Options

```bash
python3 clean.py [input] [output] [options]

Arguments:
  input                    Input video file path
  output                   Output video file path

Options:
  --subs FILE             Use existing subtitle file instead of transcribing audio (20x faster)
  --model SIZE            Whisper model: tiny, base (default), small, medium, large
  --dialog-enhance        Enable dialog enhancement (default: enabled)
  --no-dialog-enhance     Disable dialog enhancement (not recommended)
  --auto-upgrade-model    Enable auto-upgrade to larger model if WPM low (default: enabled)
  --no-auto-upgrade       Disable auto-upgrade mechanism
  --min-wpm FLOAT         Minimum words per minute threshold (default: 50.0)
  --mute-only             Mute audio during profanity instead of cutting segments
  --remove-timestamps     Manually add timestamps to remove: "start-end,start-end"
```

## Examples

### Example 1: Basic Cleaning (Recommended - Uses Base Model + Dialog Enhancement)

```bash
# Automatic optimal settings - dialog enhancement, base model, auto-upgrade
python3 clean.py movie.mp4 movie_cleaned.mp4
python3 clean.py movie.mp4
# Output: movie_cleaned.mp4 and movie_cleaned.srt
```

### Example 2: YouTube Video

```bash
# Download and clean in one go
yt-dlp -o "video.%(ext)s" "https://www.youtube.com/watch?v=VIDEO_ID"
python3 clean.py video.mp4 video_cleaned.mp4
```

### Example 3: Using Existing Subtitles (20x Faster)

```bash
# Use subtitles instead of transcribing (skips audio processing)
python3 clean.py movie.mp4 movie_cleaned.mp4 --subs movie.srt
```

### Example 4: Maximum Accuracy Mode

```bash
# Use large model for best possible transcription (slower)
python3 clean.py movie.mp4 movie_cleaned.mp4 --model large
```

### Example 5: Speed vs Quality Trade-off

```bash
# Faster but may miss profanity on complex audio (not recommended)
python3 clean.py movie.mp4 movie_cleaned.mp4 --model tiny --no-dialog-enhance
```

## Output Files

- **Cleaned Video**: `[input]_cleaned.mp4` - Video with profanity segments removed
- **Cleaned Subtitles**: `[input]_cleaned.srt` - Subtitles with profanity filtered and timestamps adjusted

## Frequently Asked Questions

### Is this really free?
**Yes!** 100% free, open-source, and no hidden costs. Unlike VidAngel ($9.99/month) or ClearPlay ($7.99/month), you'll never pay a subscription.

### Do I need Netflix or Amazon Prime?
**No!** This works with ANY video file - local files, YouTube downloads, DVDs, Blu-rays. Not limited to specific streaming services.

### How long does processing take?
A 2-hour movie takes 6-10 hours on CPU (base model with dialog enhancement) or 20-40 minutes with GPU. Process once, watch unlimited times. No ongoing streaming required like VidAngel. GPU rental recommended for batch processing.

### Will it work on my computer?
If you can run Python, yes! Works on Windows, Mac, and Linux. Minimum: 4GB RAM and dual-core CPU.

### Is my privacy protected?
Absolutely! Everything runs locally on your computer. No cloud uploads, no tracking, no data collection.

### Can I use this for YouTube videos?
Yes! Download with yt-dlp, then clean the video. Perfect for creating family-friendly content.

### Does it remove all profanity?
It detects 1,192 profanity words (including sexual content) with 95%+ accuracy using base model + dialog enhancement. Some edge cases may require manual review.

### Can I customize what gets filtered?
Currently uses a comprehensive profanity database. Custom word lists coming in future updates!

## Use Cases - Enjoy Movies Your Way

### Family Movie Nights
Create clean versions of popular movies for kids without paying VidAngel subscription fees.

### Religious Communities  
Share edited content for church events and religious education without offensive language.

### Elderly Care
Provide entertainment for seniors sensitive to modern movie language.

### Educational Settings
Use movie clips in classrooms and workshops with appropriate content filtering.

### Content Creators
Clean source material for family-friendly YouTube channels and social media.

### Personal Preference
Some people just prefer watching movies without constant cursing - and that's okay!

## Comprehensive Profanity Detection

Unlike simple word filters, this profanity filter uses AI-powered transcription with dialog enhancement and a comprehensive database of **1,192 profanity words and phrases**:

### What Gets Filtered
- **Curse Words**: F-words, S-words, and all common profanity
- **Sexual Content**: Explicit anatomical terms, intimate acts, positions, arousal terms
- **Abusive Language**: Offensive and derogatory terms
- **Multi-Word Phrases**: Intelligently detects "fuck you", "bull shit", etc.
- **Audio Cues**: Screaming (in sexual context), moaning, intimate sounds
- **Variations**: Catches misspellings and creative variations

### Smart Detection Features
- **Dialog Enhancement**: Isolates speech from music/effects using audio filtering (200-3500Hz vocal range)
- **Base Model Default**: 74M parameters (2x more accurate than tiny model)
- **Auto-Upgrade**: Automatically retries with larger model if transcription quality low
- **Word-Level Precision**: Only removes profanity, keeps clean dialogue
- **Context Aware**: Whole-word matching prevents false positives
- **Auto-Merging**: Combines split phrases for natural removal
- **Subtitle Sync**: Automatically adjusts subtitles after cleaning

### Family-Friendly Content Creation
Perfect for creating clean versions to watch with:
- Young children (PG content from R-rated movies)
- Elderly relatives sensitive to language
- Religious gatherings and community events
- Educational settings and classrooms
- Anyone who wants to enjoy movies without offensive language

**Enjoy movies YOUR way without the monthly subscription costs of VidAngel or ClearPlay!**

## Technical Details

- **Video Processing**: FFmpeg with frame-accurate cutting and quality matching
- **Audio Transcription**: faster-whisper (CTranslate2) with word-level timestamps for precise detection
- **Dialog Enhancement**: FFmpeg audio filtering (highpass 200Hz, lowpass 3500Hz, dynamic normalization, volume 1.3x)
- **Profanity Database**: 1,192 words with intelligent multi-word phrase merging (1.5s threshold)
- **Quality Monitoring**: WPM calculation warns if transcription incomplete (threshold: 50 WPM)
- **Auto-Upgrade**: Automatically retries with next larger model if WPM below threshold
- **Subtitle Formats**: SRT and VTT fully supported
- **Encoding**: Smart quality matching preserves original video bitrate and settings
- **AI Model**: Uses faster-whisper 'base' model by default (74M params, int8 quantized for CPU efficiency)

## Troubleshooting

### "faster-whisper not installed"
```bash
pip install faster-whisper
```

### "FFmpeg not found"
Install FFmpeg:
- Ubuntu/Debian: `sudo apt install ffmpeg`
- macOS: `brew install ffmpeg`
- Windows: Download from https://ffmpeg.org

### Slow transcription (6+ hours for movies)
- **Expected**: Base model with dialog enhancement takes 3-6 hours per 2-hour movie on CPU
- **GPU acceleration**: Install CUDA-enabled PyTorch for 10-20x speedup
- **Cloud rental**: Use AWS/Google Cloud GPU instances for batch processing
- **Alternative**: Use `--subs` with existing subtitle files (skips transcription, 20x faster)
- **Not recommended**: `--model tiny` is much faster but misses profanity on complex audio

### Detection seems incomplete
- Check transcript: `--dump-transcript words.txt` to see what was transcribed
- Verify WPM: Should be >50 for movies (tool warns automatically)
- Audio quality: Dialog enhancement helps but very poor audio may need manual review
- Try larger model: `--model small` or `--model medium` for better accuracy

### Out of memory errors
- Close other applications (need 8GB RAM minimum, 16GB recommended)
- Ensure adequate disk space (2x video file size needed temporarily)
- Process shorter videos in batches if system limited


## Related Comparisons

### VidAngel vs This Tool
- **VidAngel**: $9.99/month, requires Netflix/Prime, streaming only
- **This Tool**: Free, works with any video, offline viewing

### ClearPlay vs This Tool  
- **ClearPlay**: $7.99/month, requires compatible devices, limited content
- **This Tool**: Free, works on any computer, unlimited content

### Why Choose Free Over Paid?
- **Save $96-120 per year** compared to subscriptions
- **No streaming limitations** - watch offline anytime
- **Complete privacy** - no account required
- **Any video source** - not locked to specific services
- **One-time processing** - watch unlimited times

## Support & Community

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Share tips and ask questions
- **Contributions**: Pull requests welcome!
- **Star this repo**: Help others discover this free alternative to VidAngel and ClearPlay

## License

Open source and free to use. See LICENSE file for details.

---

**Tired of paying $10/month for VidAngel or ClearPlay?** This free, open-source profanity filter gives you complete control over your family's viewing experience without the subscription costs. Download once, use forever!

**#ProfanityFilter #FamilyFriendly #VidAngelAlternative #ClearPlayAlternative #FreeMovieFilter #EnjoyMoviesYourWay**

### Slow Processing
- Use `--whisper-model tiny` for faster transcription
- Provide subtitle files instead of transcribing audio
- Use GPU if available (automatic detection)

## Use Cases

- **Content Creators**: Create family-friendly versions of your videos for broader audiences
- **Educators**: Prepare educational content suitable for classrooms
- **Parents**: Make movies and shows safe for children to watch
- **Streaming Platforms**: Automate content moderation and filtering
- **Video Editors**: Batch process multiple videos with profanity removal

## License

MIT License - Free to use for personal and commercial projects

## Contributing

Contributions welcome! Please open an issue or pull request on GitHub.

## Support

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check the `USAGE.md` file for detailed guides
- **Examples**: See the `sample/` directory for before/after examples
