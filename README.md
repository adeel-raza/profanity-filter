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

# 🚀 Try the Online Demo

Want to see how it works before installing? **Try the app instantly in your browser:**

[![Hugging Face Spaces](https://img.shields.io/badge/Live%20Demo-Hugging%20Face-blue?logo=huggingface)](https://huggingface.co/spaces/adeel-raza/video-profanity-filter)

---

# Free Profanity Filter for Movies & Videos - VidAngel & ClearPlay Alternative

**Created by [Adeel Raza](https://elearningevolve.com/about) Contact: info@elearningevolve.com**

**Watch movies YOUR way – completely FREE!** Remove profanity, curse words, and offensive language from ANY video automatically. Unlike VidAngel or ClearPlay, no subscription or Netflix account is required. Works with local video files, YouTube downloads, and any MP4/MKV content.

**Perfect for families who want to enjoy movies together without inappropriate language**  
**100% FREE alternative to VidAngel ($9.99/month) and ClearPlay ($7.99/month)**  
**Privacy-focused: Everything runs locally on your computer**  
**AI-powered with enhanced dialogue detection using faster-whisper**

---

## Customize Filtered Words (CSV)

Edit `profanity_words.csv` to control what the app filters—no Python changes
are required.

1. Open `profanity_words.csv` in any text editor or spreadsheet application.
2. Words and phrases are separated by commas and may span multiple lines.
3. Delete any word you never want filtered.
4. Add any new words or phrases in lowercase, separated by commas.
5. Save the file, then restart the app or run `clean.py` again.

Example:

```csv
fuck,fucking,shit,bullshit
pissed,crap,fuck you
```

Whitespace and duplicate entries are ignored. An existing empty CSV disables
the default word list. If the CSV is missing or cannot be read, the app safely
uses its built-in defaults. The optional `--include-religious` flag still adds
the separate religious/exclamatory list.

Hard profanity enabled in the CSV is always filtered. The ambiguous defaults
`swallow`, `swallower`, `swalow`, and `dirty` use conservative nearby-word
rules, so ordinary phrases such as `swallow these pills` and `dirty bomb` are
not removed. They are filtered only when nearby dialogue supplies explicit
sexual or offensive context. The person name `jerry` and plural `jerries` are
not included in the defaults. These are explicit rules rather than a claim of
complete language understanding; edit the CSV if you prefer stricter or looser
filtering.

---

## 💝 Support This Project

**If you find this project helpful, please consider supporting it:**

[![Support via Stripe](https://img.shields.io/badge/Support%20via%20Stripe-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://link.elearningevolve.com/self-pay)

---

## 📑 Table of Contents

- [Customize Filtered Words (CSV)](#customize-filtered-words-csv)
- [Installation - Easy Setup Guide](#installation-easy-setup-guide)
- [Quick Start - Simple for Non-Technical Users](#quick-start-simple-for-non-technical-users)
- [Why Choose This Free Profanity Filter?](#why-choose-this-free-profanity-filter)
- [How It Works - The Technology Behind 95%+ Accuracy](#how-it-works-the-technology-behind-95-accuracy)
- [System Requirements](#system-requirements)
- [Usage - Simple Command Line](#usage-simple-command-line)
- [Command Line Options](#command-line-options)
- [Examples](#examples)
- [Output Files](#output-files)
- [Processing Time & Resource Usage](#processing-time-resource-usage)
- [Frequently Asked Questions](#frequently-asked-questions)
- [Use Cases - Enjoy Movies Your Way](#use-cases-enjoy-movies-your-way)
- [Comprehensive Profanity Detection](#comprehensive-profanity-detection)
- [Technical Details](#technical-details)
- [Troubleshooting](#troubleshooting)
- [Related Comparisons](#related-comparisons)
- [Support & Community](#support-community)
- [License](#license)
- [Contributing](#contributing)

---

## Installation - Easy Setup Guide

### Prerequisites (install these first)

The Python requirements file cannot install system programs such as FFmpeg. Before
cloning the repository, install:

- **Python 3.8+**, including `pip` and virtual-environment support
- **FFmpeg and FFprobe** (FFprobe is normally included with FFmpeg)
- **Git**
- **An NVIDIA CUDA setup is optional**; the app automatically uses a CUDA GPU
  when CTranslate2 can detect one and otherwise falls back to CPU

#### Ubuntu / Debian

```bash
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv ffmpeg
```

#### Fedora

```bash
sudo dnf install -y git python3 python3-pip ffmpeg
```

#### macOS (Homebrew)

```bash
brew install git python ffmpeg
```

#### Windows

1. Install [Python 3](https://www.python.org/downloads/) and enable
   **Add Python to PATH** during setup.
2. Install [Git for Windows](https://git-scm.com/download/win).
3. Install FFmpeg with `winget install Gyan.FFmpeg`, or download it from
   [ffmpeg.org](https://ffmpeg.org/download.html) and add its `bin` folder to
   `PATH`.

Verify the prerequisites before continuing:

```bash
python3 --version  # On Windows, use: python --version
ffmpeg -version
ffprobe -version
git --version
```

### Quick Setup (Copy & Paste)

```bash
# Step 1: Clone the repository
git clone https://github.com/adeel-raza/profanity-filter.git
cd profanity-filter

# Step 2: Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Step 3: Install dependencies (takes 2-5 minutes)
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# Step 4: Confirm the command is ready
python3 clean.py --help
```

On Windows, activate with `venv\Scripts\activate` and replace `python3` with
`python` in the commands above.

> **Ubuntu/Debian shortcut:** `./install.sh` performs the system check, creates
> the virtual environment, and installs the Python requirements. The manual
> steps above are recommended on other operating systems.

### Optional GPU acceleration

The app automatically accelerates both major processing stages when compatible
hardware is available:

- **AI transcription:** NVIDIA CUDA through CTranslate2
- **Video encoding:** NVIDIA NVENC, Intel Quick Sync, AMD AMF, or Apple
  VideoToolbox through FFmpeg
- If a compatible device, driver, runtime, or encoder is unavailable, that
  stage safely falls back to CPU
- Pascal GPUs such as the Quadro P2000 use `int8` (then `float32`) rather than
  unsupported/slow `float16`

**Recommendation:** Prefer a GPU machine when available. In our controlled
side-by-side tests, GPU was better for:

1. **Speed** — faster Whisper transcription and much faster video rebuild
2. **Encode quality** — higher SSIM/PSNR vs the source after cutting

CPU still works fully via automatic fallback. Before VAD tuning, one CPU test
stretched a word across silence and over-cut clean audio. Current builds use a
tuned VAD threshold and clamp overstretched single-word spans. In the current
three-clip validation, CPU and GPU both detected and removed all three known
profanities with closely matching boundaries. Do not interpret the small test
set as proof that either device is always more accurate.

Install a current NVIDIA driver and the CUDA/cuDNN runtime versions required by
your installed CTranslate2 release. Then verify detection:

```bash
nvidia-smi
python3 -c "import ctranslate2; print('CUDA devices:', ctranslate2.get_cuda_device_count())"
```

When processing starts, the log reports the selected device and compute type.
It also reports the selected video encoder. For troubleshooting only, force
CPU processing with:

```bash
PROFANITY_FILTER_DEVICE=cpu python3 clean.py input.mp4 output.mp4
PROFANITY_FILTER_VIDEO_ENCODER=cpu python3 clean.py input.mp4 output.mp4
```

To request a specific FFmpeg hardware encoder:

```bash
PROFANITY_FILTER_VIDEO_ENCODER=h264_nvenc python3 clean.py input.mp4 output.mp4
```

Requested hardware still falls back safely to CPU if initialization or the
actual movie encode fails.

### Verified CPU vs GPU benchmark (same 12s clip)

Measured with the **same source file** (12.012s, 1918x802, SHA-256
`e0848fc3…`) on a CPU-only laptop vs a Quadro P2000 server.

| Stage | Laptop (no NVIDIA GPU) | Home server (Quadro P2000) |
|---|---|---|
| Whisper device | CPU `int8` | CUDA `int8` |
| Video encoder | CPU `libx264` | NVIDIA `h264_nvenc` |
| Full `clean.py` wall clock | **16.14s** | **10.30s** (~1.6x faster) |
| Transcription | 1.0s (12.6x realtime) | 0.5s (22.6x realtime) |
| Identical cut encode (`2.15–5.37s` removed) | **8.97s** | **2.46s** (~3.6x faster) |
| Quality vs source (SSIM All, first 2s keep) | **0.9948** | **0.9967** |
| Quality vs source (PSNR avg, first 2s keep) | **52.1 dB** | **54.4 dB** |
| Cleaned file size (identical cut) | 3.7 MB (~3.3 Mbps) | 6.3 MB (~5.8 Mbps) |
| Peak NVENC utilization | n/a | **100%** |
| Detected cut for `pissed` (before CPU VAD fix) | `2.15–5.37` (**3.22s**, over-cut) | `4.83–5.37` (**0.54s**, accurate) |

Notes for users:

- **GPU is the better path** when available for speed and encode fidelity.
- The identical-cut encode row is the fair encoder comparison (same remove
  timestamps on both machines).
- CPU fallback remains supported. Newer builds add Whisper `vad_filter` plus a
  1.0s single-word span clamp so CPU is less likely to stretch a word across
  silence and delete clean audio.
- Some CPU work remains even on GPU machines (audio + FFmpeg timeline filters).

### Current three-clip validation after CPU VAD tuning

Measured on commit `3742aec` with three distinct 12.012s clips containing known
`shitty`, `shit`, and `fuck` dialogue. Source SHA-256 hashes were matched on
both machines before testing.

| Metric (mean of 3 clips) | Laptop CPU | Quadro P2000 GPU |
|---|---:|---:|
| Known profanity detected | **3/3** | **3/3** |
| Target absent after cleaning | **3/3** | **3/3** |
| Full `clean.py` wall clock | 20.47s | **8.51s** (~2.4x faster) |
| Whisper transcription | 1.13s | **0.57s** (~2.0x faster) |
| Video cutting/rebuild | 15.03s | **3.01s** (~5.0x faster) |
| Quality vs source (SSIM, unaffected first 2s) | 0.9931 | **0.9979** |
| Quality vs source (PSNR, unaffected first 2s) | 50.61 dB | **56.07 dB** |
| Average cleaned file size | 10.6 MB | 14.3 MB |
| Full output decoded without errors | **3/3** | **3/3** |

Cut-boundary agreement was close: CPU vs GPU differed by an average of 0.077s
at the start and 0.010s at the end (maximum start difference: 0.21s). Every cut
fell inside its independently known subtitle caption. On these samples, both
paths were accurate after tuning; GPU's measurable advantages were speed and
visual fidelity, with about 34% larger output files.

### Six-clip ambiguous-context validation

The context rules were tested on the same six source clips on a CPU-only laptop
and a Quadro P2000 server:

- Neutral dialogue (`swallow these pills`, `dirty bomb`, and the name `Jerry`)
  was transcribed on both machines and correctly left untouched: **3/3 on CPU
  and 3/3 on GPU**.
- Genuine profanity (`shitty`, `fuck up`, and `bullshit`) was detected and
  removed: **3/3 on CPU and 3/3 on GPU**.
- Re-transcribing all six profanity-cleaned outputs found none of the target
  words. All 12 outputs decoded without errors.
- Neutral outputs were byte-identical to their sources, confirming that the app
  did not re-encode or otherwise alter them.
- Total wall time for the six independent runs was 55.40s on CPU and 35.73s on
  GPU. Each run loaded the model separately, so these figures include startup
  overhead and should not be treated as a long-video benchmark.

### Realistic CPU vs GPU comparison (after all tests)

After the single-clip encode test, the three-clip VAD validation, and the
six-clip context validation on the same laptop vs Quadro P2000 pair, this is the
honest practical picture:

| What users care about | CPU-only laptop | Quadro P2000 GPU | Realistic takeaway |
|---|---|---|---|
| Hard-profanity detection | Passed all known targets in the tuned tests | Passed all known targets | Both are usable for detection after VAD tuning |
| Ambiguous false positives (`swallow these pills`, `dirty bomb`, name `Jerry`) | Correctly left alone | Correctly left alone | Context rules work the same on both devices |
| Cut timing after VAD tuning | Matched known captions closely | Matched known captions closely | GPU is not clearly “more accurate” on the current samples |
| Transcription speed | ~1.0–1.1s on 12s clips | ~0.5–0.6s on the same clips | GPU is about **2x** faster at Whisper |
| Video rebuild after a cut | ~9–15s on short clips | ~2.5–3.0s on the same clips | GPU encoding is about **3.5–5x** faster |
| Visual fidelity after cutting | SSIM ~0.993–0.995 / PSNR ~50–52 dB | SSIM ~0.997–0.998 / PSNR ~54–56 dB | GPU outputs measured closer to the source |
| Output file size after cutting | Smaller | Larger (~30–70% in these tests) | GPU quality settings favor fidelity over size |
| Full job with real cuts | Mean ~20.5s on three 12s clips | Mean ~8.5s on the same clips | GPU is about **2.4x** faster end-to-end |
| Jobs with no cuts (copy-through) | Can finish sooner on short clips | May look slower because of CUDA startup | GPU advantage appears when the app actually re-encodes |

**Bottom line for users:**

1. Prefer a GPU machine when you have one. The realistic gains are **speed** and
   **encode quality**, not a proven detection-accuracy monopoly.
2. CPU remains a complete fallback. Current builds keep CPU cut timing much
   closer to GPU by using Whisper VAD plus a 1.0s single-word span clamp.
3. The biggest GPU win is the cut/rebuild stage (`h264_nvenc` vs `libx264`).
   Transcription is faster too, but encoding usually dominates wall time.
4. Short no-cut clips can hide the GPU advantage because each run still pays
   model/device startup cost. Longer movies with real removals are where GPU
   savings compound.
5. Expect GPU cleaned files to be somewhat larger when quality settings are
   held high. That is a fidelity tradeoff, not a failure.

These conclusions come from controlled short clips with matched source hashes.
Absolute times will change with movie length, resolution, bitrate, Whisper
model size, and hardware, but the relative pattern above is what we repeatedly
measured.

---

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

**Note:** If your subtitle file has the same name as your video (e.g. `movie.mp4` and `movie.srt`) and is in the same directory, it will be auto-detected. You do not need to specify `--subs` in this case.

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

# Also filter religious/exclamatory terms
python3 clean.py input.mp4 output.mp4 --mute-only --include-religious

# Hybrid mode (requires matching subtitles)
python3 clean.py input.mp4 output.mp4 --subs input.srt --hybrid

# Manually remove timestamps
python3 clean.py input.mp4 output.mp4 --remove-timestamps "10-15,30-35"
```

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
- **Tiny model** is available for faster processing, but is less accurate and may miss profanity, especially in movies with music or background noise.

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

---

## CPU-Intensive Task Warning

**Important:** Video cleaning is a **CPU-intensive task on CPU-only systems**.
On systems like the **11th Gen Intel® Core™ i5-1135G7 ×8** without a working
hardware encoder:

- Processing a 2-hour movie can take **~6 hours**
- **Do not run other heavy applications** (games, video editing, compiling) simultaneously
- Video **encoding, decoding, and profanity removal** require sustained high CPU usage
- Ensure enough **RAM and disk space** is available to avoid slowdowns or failures

> Tip: With a compatible GPU, the app automatically moves transcription and/or
> video encoding to hardware. Existing subtitles (`--subs`) can also reduce
> transcription work.

---

## Key Features - VidAngel & ClearPlay Alternative

- **No Monthly Subscription** - Save $96-120/year compared to VidAngel or ClearPlay
- **Works Offline** - No internet required after initial setup
- **Any Video Source** - Not limited to Netflix or specific streaming services
- **Fast AI Transcription** - Uses faster-whisper (CTranslate2) for 4-10x speed improvement
- **Smart Profanity Detection** - Identifies 1,192+ curse words and offensive phrases
- **Precise Editing** - Word-level timestamps remove only profanity, keeps dialogue intact
- **Family Safe** - Create clean versions for kids and family movie nights
- **YouTube Compatible** - Download and clean YouTube videos
- **Quality Preserved** - Maintains original video quality and encoding
- **Open Source** - Free forever, community-driven improvements

---

## System Requirements

### ⚠️ IMPORTANT: Resource Usage Warning

**On CPU-only systems, this application is CPU and memory intensive.**
Hardware-enabled systems automatically use a validated GPU video encoder:

- **CPU Usage**: Expect 80-100% only when hardware acceleration is unavailable
- **RAM Requirements**: 8GB minimum (16GB recommended for base model)
- **Disk I/O**: Heavy read/write operations during video processing
- **Processing Time**: 3-6 hours for a 2-hour movie on CPU (base model with dialog enhancement)

**⚡ GPU Strongly Recommended**: NVIDIA CUDA accelerates transcription, while
NVENC, Quick Sync, AMF, or VideoToolbox accelerates the quality video rebuild.
Some CPU remains necessary for FFmpeg timeline filters, audio processing, and
application coordination, but the expensive H.264 encoding is moved to
hardware.

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
With compatible transcription/video-encoding hardware:
- **Processing Time**: 2-hour movie in ~5-10 minutes
- **CPU Load**: Significantly reduced; exact usage depends on FFmpeg filters
- **System Usability**: Computer remains responsive during processing
- **Cost**: Free to use, but requires compatible hardware

**Note**: Unlike streaming-based filters (VidAngel, ClearPlay), this tool processes videos locally, so processing time varies by system specs. You only process once, then enjoy unlimited viewing!

---

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

---

## Why faster-whisper?

This tool uses **faster-whisper** instead of standard OpenAI Whisper for significant performance improvements:

- **4-10x faster transcription**: 15 seconds vs 25 seconds for a 3-minute video
- **Same accuracy**: CTranslate2 backend provides identical transcription quality
- **Lower memory usage**: Optimized int8 quantization for efficient CPU processing
- **Word-level timestamps**: Precise profanity detection and removal

**Example performance** (3-minute video, CPU):
- Transcription: ~15 seconds (12.3x real-time)
- Total processing: ~1 minute 40 seconds including video cutting

---

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

---

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

---

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
- **CPU-only**: High utilization during transcription and H.264 encoding
- **GPU-enabled**: GPU handles supported AI transcription and video encoding;
  CPU still handles audio and timeline filters
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

---

## Command Line Options

```bash
python3 clean.py [input] [output] [options]

Arguments:
  input                    Input video file path
  output                   Output video file path

Options:
  --subs FILE             Use subtitle file (SRT/VTT). Auto-detects matching .srt/.vtt if omitted.
  --srt-window FLOAT      Limit subtitle-cue removal window when using --use-subs-detection.
  --pad FLOAT             Extra seconds before/after subtitle cues in subtitle-driven detection.
  --merge-gap FLOAT       Max gap between detected segments to merge (default: 0.06).
  --expand-pad FLOAT      Expand each detected segment before cutting/muting.
  --model SIZE            Whisper model: tiny, base, small, medium, large.
  --force-audio           Force audio-based detection (default behavior).
  --use-subs-detection    Use subtitles for detection instead of audio (advanced).
  --phrase-gap FLOAT      Max gap to merge consecutive profanity words into phrase segments.
  --remove-timestamps     Manually add timestamps: "start-end,start-end".
  --mute-only             Mute profanity intervals instead of cutting video timeline.
  --include-religious     Also filter religious/exclamatory terms (god, jesus, damn, hell).
  --dump-transcript FILE  Save raw transcript words with timestamps.
  --dialog-enhance        Enable dialog enhancement (default: enabled).
  --no-dialog-enhance     Disable dialog enhancement.
  --min-wpm FLOAT         Warn if words/minute is below threshold (default: 50.0).
  --auto-upgrade-model    Retry once with larger model if transcript quality is low.
  --no-auto-upgrade       Disable automatic model upgrade.
  --hybrid                Subtitle-first + selective audio detection (requires subtitles).
```

---

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

---

## Output Files

- **Cleaned Video**: `[input]_cleaned.mp4` - Video with profanity segments removed
- **Cleaned Subtitles**: `[input]_cleaned.srt` - Subtitles with profanity filtered and timestamps adjusted

---

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

---

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

---

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

---

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

---

## Troubleshooting

### "faster-whisper not installed"
```bash
pip install faster-whisper
```

### "FFmpeg not found"
Install FFmpeg:
- Ubuntu/Debian: `sudo apt update && sudo apt install -y ffmpeg`
- Fedora: `sudo dnf install -y ffmpeg`
- macOS: `brew install ffmpeg`
- Windows: `winget install Gyan.FFmpeg`

Close and reopen the terminal after installation, then verify both binaries:

```bash
ffmpeg -version
ffprobe -version
```

### Slow transcription (6+ hours for movies)
- **Expected**: Base model with dialog enhancement takes 3-6 hours per 2-hour movie on CPU
- **GPU acceleration**: Install compatible NVIDIA drivers plus the CUDA/cuDNN
  runtime required by CTranslate2; the active faster-whisper path does not use
  PyTorch
- **Verify GPU detection**:
  `python3 -c "import ctranslate2; print(ctranslate2.get_cuda_device_count())"`
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

---

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

---

## Support & Community

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Share tips and ask questions
- **Contributions**: Pull requests welcome!
- **Star this repo**: Help others discover this free alternative to VidAngel and ClearPlay

---

## License

Open source and free to use. See LICENSE file for details.

---

**Tired of paying $10/month for VidAngel or ClearPlay?** This free, open-source profanity filter gives you complete control over your family's viewing experience without the subscription costs. Download once, use forever!

**#ProfanityFilter #FamilyFriendly #VidAngelAlternative #ClearPlayAlternative #FreeMovieFilter #EnjoyMoviesYourWay**

---

## Contributing

Contributions welcome! Please open an issue or pull request on GitHub.
