---
title: Free Profanity Filter for Movies & Videos
emoji: ""
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
 - netflix-filter
 - open-source
 - local-processing
 - privacy
---

# Try the Online Demo

Want to see how it works before installing? **Try the app instantly in your browser:**

[![Hugging Face Spaces](https://img.shields.io/badge/Live%20Demo-Hugging%20Face-blue?logo=huggingface)](https://huggingface.co/spaces/adeel-raza/video-profanity-filter)

---

# Free Profanity Filter for Movies & Videos

**Created by [Adeel Raza](https://elearningevolve.com/about) · Contact: info@elearningevolve.com**

This tool cleans **profanity and swear words** out of video files you already
have. It finds spoken offensive language with AI, then either **cuts** those
moments out or **mutes** them in place, and writes a cleaned video plus a
cleaned subtitle file.

**What it does**

- Detects mainly profanity and swear words (editable word list; optional
  stricter lists available)
- Removes matched speech by **cutting** the timeline, or keeps the timeline and
  **mutes** those intervals with `--mute-only`
- Outputs a cleaned video and a cleaned `.srt` subtitle file
- Works much faster when you provide (or auto-detect) an existing subtitle file
  alongside the video
- Runs entirely on your computer—no cloud upload and no account required
- Supports optional GPU acceleration for much faster processing

**Who it is for**

Families, educators, and anyone who wants a cleaner cut of movies or clips
without a monthly subscription or streaming lock-in.

---

## Support This Project

**If you find this project helpful, please consider supporting it:** [![Support via Stripe](https://img.shields.io/badge/Support%20via%20Stripe-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://link.elearningevolve.com/self-pay)

---

## Table of Contents

- [Why Choose This Free Profanity Filter?](#why-choose-this-free-profanity-filter)
- [How It Works - The Technology Behind 95%+ Accuracy](#how-it-works-the-technology-behind-95-accuracy)
- [Installation - Easy Setup Guide](#installation-easy-setup-guide)
- [Quick Start - Simple for Non-Technical Users](#quick-start-simple-for-non-technical-users)
- [CPU-Intensive Task Warning](#cpu-intensive-task-warning)
- [System Requirements](#system-requirements)
- [Usage - Simple Command Line](#usage-simple-command-line)
- [Why faster-whisper?](#why-faster-whisper)
- [Before/After Example](#beforeafter-example)
- [How It Works - Technical Deep Dive](#how-it-works-technical-deep-dive)
- [Processing Time & Resource Usage](#processing-time-resource-usage)
- [Command Line Options](#command-line-options)
- [Output Files](#output-files)
- [Customize Filtered Words (CSV)](#customize-filtered-words-csv)
- [Frequently Asked Questions](#frequently-asked-questions)
- [Troubleshooting](#troubleshooting)
- [Support & Community](#support-community)
- [License](#license)
- [Contributing](#contributing)

---

## Why Choose This Free Profanity Filter?

### Free and open source
No subscription. Process your own files once and watch them offline as often as
you like.

### Works with your files
- Local video files (MP4, MKV, AVI, and similar)
- YouTube downloads (via yt-dlp)
- DVDs and Blu-rays ripped to digital files
- Any source you can save as a normal video file

### Privacy and control
- Everything runs on your computer
- No cloud upload required for filtering
- You choose the word list and how aggressively to filter

---

## How It Works - The Technology Behind 95%+ Accuracy

### 1. Dialog Enhancement (Audio Preprocessing)
- **Vocal isolation**: High-pass (200Hz) and low-pass (3500Hz) filters remove music, effects, and noise
- **Dynamic normalization**: Balances quiet dialogue and loud scenes for consistent transcription
- **Result**: 4-5x more words transcribed in complex audio (music, action scenes, background noise)
- **Example**: Original tiny model caught 0 profanities in Argo → Enhanced base model caught 38 segments

### 2. AI Audio Transcription (Word-Level Precision)
- Uses **faster-whisper base model** (74M parameters) for superior accuracy on movies
- **Dialog-enhanced audio** helps model "hear" speech masked by soundtracks
- Each word gets a **precise timestamp** (accurate to 0.1 seconds)
- Example: a flagged word at 79.76s-80.08s, the next word at 80.08s-80.88s
- Unlike subtitle-based filters that cut entire sentences, this tool can cut only the matched words.
- **Tiny model** is available for faster processing, but is less accurate and may miss profanity, especially in movies with music or background noise.

### 3. Smart Multi-Word Detection (Phrase Recognition)
- Automatically detects **1,000+** entries from the editable word list (including common variations)
- **Intelligent merging**: Combines split multi-word phrases into single cuts
- **Context-aware**: Uses a short time window to catch phrases spoken together
- **Whole-word matching**: Avoids matching clean words that only contain a partial letter pattern
- **Quality monitoring**: WPM (words per minute) diagnostic warns if transcription incomplete

### 4. Frame-Accurate Video Cutting
- **FFmpeg-powered editing**: Industry-standard video processing tool
- **Surgical precision**: Removes only profanity segments (typically 0.3-2 seconds each)
- **Quality preservation**: Original video bitrate, resolution, and encoding maintained
- **Smooth transitions**: Seamless cuts without audio glitches or visual artifacts

### Result: 95%+ Profanity-Free Videos

Detection covers **spoken content only** (transcription + word list). Non-verbal sounds without spoken words are not classified.
- **38 segments detected** in Argo (129-minute movie with orchestral score)
- **0.46 minutes removed** (99.6% of content preserved)
- **Improvement**: Tiny model missed 100% of profanity → Enhanced base caught all instances
- **Manual review option**: Add timestamps with `--remove-timestamps` for any missed words

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
python3 --version # On Windows, use: python --version
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
source venv/bin/activate # On Windows: venv\Scripts\activate

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

### Docker (no local Python setup)

One Dockerfile provides **two build targets**:

| Target | When to use | Build |
|---|---|---|
| `cpu` (default) | Most users / no NVIDIA GPU | `docker build -t profanity-filter:cpu --target cpu .` |
| `gpu` | NVIDIA GPU + [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) | `docker build -t profanity-filter:gpu --target gpu .` |

**Clean a video (CPU):**

```bash
docker build -t profanity-filter:cpu --target cpu .
docker run --rm \
 -v "$PWD":/data \
 -v profanity-hf-cache:/cache \
 profanity-filter:cpu \
 /app/clean.py /data/input.mp4 /data/output.mp4
```

**Clean a video (GPU):**

```bash
docker build -t profanity-filter:gpu --target gpu .
docker run --rm --gpus all \
 -v "$PWD":/data \
 -v profanity-hf-cache:/cache \
 profanity-filter:gpu \
 /app/clean.py /data/input.mp4 /data/output.mp4
```

**Optional Gradio web UI** (http://localhost:7860):

```bash
# CPU
docker run --rm -p 7860:7860 -v "$PWD":/data -v profanity-hf-cache:/cache \
 profanity-filter:cpu /app/app.py

# GPU
docker run --rm --gpus all -p 7860:7860 -v "$PWD":/data -v profanity-hf-cache:/cache \
 profanity-filter:gpu /app/app.py
```

Or with Compose:

```bash
docker compose up --build web # CPU UI
docker compose --profile gpu up --build web-gpu # GPU UI
```

Notes:

- Mount your videos into `/data` (container working directory).
- The `/cache` volume stores downloaded Whisper models so they are not re-fetched every run.
- Force CPU inside any image with `-e PROFANITY_FILTER_DEVICE=cpu`.
- The GPU image still falls back to CPU if no GPU is available at runtime.

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

1. **Speed**— faster Whisper transcription and much faster video rebuild
2. **Encode quality**— higher SSIM/PSNR vs the source after cutting

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
| Detected cut for a single swear word (before CPU VAD fix) | `2.15–5.37` (**3.22s**, over-cut) | `4.83–5.37` (**0.54s**, accurate) |

Notes for users:

- **GPU is the better path** when available for speed and encode fidelity.
- The identical-cut encode row is the fair encoder comparison (same remove
 timestamps on both machines).
- CPU fallback remains supported. Newer builds add Whisper `vad_filter` plus a
 1.0s single-word span clamp so CPU is less likely to stretch a word across
 silence and delete clean audio.
- Some CPU work remains even on GPU machines (audio + FFmpeg timeline filters).

### Realistic CPU vs GPU comparison (after all tests)

After the single-clip encode test, the three-clip VAD validation, and the
six-clip context validation on the same laptop vs Quadro P2000 pair, this is the
honest practical picture:

| What users care about | CPU-only laptop | Quadro P2000 GPU | Realistic takeaway |
|---|---|---|---|
| Hard-profanity detection | Passed all known targets in the tuned tests | Passed all known targets | Both are usable for detection after VAD tuning |
| Ambiguous false positives (ordinary phrases / common name) | Correctly left alone | Correctly left alone | Context rules work the same on both devices |
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

Tip: providing a subtitle file (or placing `movie.srt` next to `movie.mp4`) makes cleaning much faster because less audio transcription is needed.

### Clean a Video
```bash
python3 clean.py YourMovie.mp4 YourMovie_cleaned.mp4
# Output: YourMovie_cleaned.mp4 and YourMovie_cleaned.srt
```

### Use Subtitle Files for Faster Processing

If a matching `.srt` / `.vtt` sits next to the video (same filename), it is
auto-detected. Passing subtitles skips or reduces transcription work and is
usually much faster than audio-only cleaning.

```bash
python3 clean.py YourMovie.mp4 YourMovie_cleaned.mp4 --subs YourMovie.srt
```

**Note:** If your subtitle file has the same name as your video (e.g. `movie.mp4` and `movie.srt`) and is in the same directory, it will be auto-detected. You do not need to specify `--subs` in this case.

### Download & Clean YouTube Video
```bash
yt-dlp -o "video.mp4" "https://www.youtube.com/watch?v=VIDEO_ID"
python3 clean.py video.mp4 video_cleaned.mp4
```

### More options

See [Usage](#usage---simple-command-line) and [Command Line Options](#command-line-options) for mute mode, model size, hybrid detection, and other flags.

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

## System Requirements

### Important: Resource Usage Warning

**On CPU-only systems, this application is CPU and memory intensive.**
Hardware-enabled systems automatically use a validated GPU video encoder:

- **CPU Usage**: Expect 80-100% only when hardware acceleration is unavailable
- **RAM Requirements**: 8GB minimum (16GB recommended for base model)
- **Disk I/O**: Heavy read/write operations during video processing
- **Processing Time**: 3-6 hours for a 2-hour movie on CPU (base model with dialog enhancement)

**GPU Strongly Recommended**: NVIDIA CUDA accelerates transcription, while
NVENC, Quick Sync, AMF, or VideoToolbox accelerates the quality video rebuild.
Some CPU remains necessary for FFmpeg timeline filters, audio processing, and
application coordination, but the expensive H.264 encoding is moved to
hardware.

**Best Practice**: Run this tool overnight or when you don't need your computer. Close unnecessary applications before processing. Consider GPU rental services (AWS, Google Cloud) for batch processing.

### Minimum Specs (Budget PCs)
- **CPU**: Quad-core processor (Intel i5, AMD Ryzen 5, or better)
- **RAM**: 8GB minimum (base model)
- **Storage**: 5GB free space + 2x video file size
- **OS**: Windows 10/11, macOS 10.15+, or Linux
- **Processing Time**: 2-hour movie takes ~6 hours on CPU
- **Warning:** Expect very long processing times without GPU

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

**Note**: This tool processes videos locally, so runtime depends on your hardware. Process a file once, then watch the cleaned copy as often as you like.

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
python3 clean.py input.mp4 output.mp4 --model small # or medium, large

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

**New defaults (much stronger detection):**

- Base model (74M parameters) - 2x more accurate
- Dialog enhancement enabled - isolates speech
- Auto-upgrade if WPM low - catches edge cases
- 1,000+ entries in the default word list

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

See the tool in action with our sample video.

### Sample Video Results
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
 [79.76s-80.08s] "<flagged-word>"
 [80.08s-80.88s] "<next-word>"
 [82.15s-82.67s] "<flagged-word>"
 ```
- **Why accurate**: Trained on 680,000 hours of multilingual speech data
- **Speed**: Processes at 10-12x real-time speed on modern CPUs

#### Step 2: Word-List Matching
- **Database**: Editable CSV with 1,000+ default entries (plus optional soft list)
- **Matching**: Whole-word exact matching (helps prevent false positives)
- **Scope**: Filters **spoken** words/phrases that appear in the transcript and
 match the word list—not separate audio-event / sound classification

#### Step 3: Intelligent Phrase Merging
- **Problem**: AI sometimes splits a multi-word phrase across separate detections
- **Solution**: Automatically merges nearby detections into a single cut
- **Result**: More natural speech flow, fewer awkward gaps

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
- **1,000+ word database** (editable CSV; optional soft list available)
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
- Non-verbal sounds are not detected—only spoken words that appear in the transcript
- **Solution**: Use `--remove-timestamps` to manually add missed segments; edit `profanity_words.csv` for custom spoken terms

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
 input Input video file path
 output Output video file path

Options:
 --subs FILE Use subtitle file (SRT/VTT). Auto-detects matching .srt/.vtt if omitted.
 --srt-window FLOAT Limit subtitle-cue removal window when using --use-subs-detection.
 --pad FLOAT Extra seconds before/after subtitle cues in subtitle-driven detection.
 --merge-gap FLOAT Max gap between detected segments to merge (default: 0.06).
 --expand-pad FLOAT Expand each detected segment before cutting/muting.
 --model SIZE Whisper model: tiny, base, small, medium, large.
 --force-audio Force audio-based detection (default behavior).
 --use-subs-detection Use subtitles for detection instead of audio (advanced).
 --phrase-gap FLOAT Max gap to merge consecutive profanity words into phrase segments.
 --remove-timestamps Manually add timestamps: "start-end,start-end".
 --mute-only Mute profanity intervals instead of cutting video timeline.
 --include-religious Also filter religious/exclamatory terms (off by default).
 --dump-transcript FILE Save raw transcript words with timestamps.
 --dialog-enhance Enable dialog enhancement (default: enabled).
 --no-dialog-enhance Disable dialog enhancement.
 --min-wpm FLOAT Warn if words/minute is below threshold (default: 50.0).
 --auto-upgrade-model Retry once with larger model if transcript quality is low.
 --no-auto-upgrade Disable automatic model upgrade.
 --hybrid Subtitle-first + selective audio detection (requires subtitles).
```

---

## Output Files

- **Cleaned Video**: `[input]_cleaned.mp4` - Video with profanity segments removed
- **Cleaned Subtitles**: `[input]_cleaned.srt` - Subtitles with profanity filtered and timestamps adjusted

---

## Customize Filtered Words (CSV)

Edit `profanity_words.csv` to add or remove words the tool should filter.
Open it in any text editor or spreadsheet, save your changes, and they take
effect the next time you run `clean.py` or restart the Gradio app.

1. Open `profanity_words.csv`.
2. Words and phrases are separated by commas and may span multiple lines.
3. Delete any word you never want filtered.
4. Add new words or phrases in lowercase, separated by commas.
5. Prefix a token with `#` to treat it as a comment (that entry is ignored).
6. Save the file, then run `clean.py` again (or restart the Gradio app).

Example:

```csv
word-one,word-two,phrase one
another-term
# notes-or-disabled-entry
```

Whitespace and duplicate entries are ignored. An empty CSV disables the default
word list. If the CSV is missing or cannot be read, the app falls back to its
built-in defaults.

**Religious / exclamatory terms** are off by default. Include them with:

```bash
python3 clean.py input.mp4 output.mp4 --include-religious
```

Clear matches from your word list are always filtered. A small set of
context-sensitive words uses nearby-dialogue rules so ordinary, non-offensive
phrases are less likely to be muted. Edit the CSV if you prefer stricter or
looser filtering.

### Optional soft / romance vocabulary

The default `profanity_words.csv` focuses on clearly offensive language, so
ordinary dialogue is less likely to be muted.

Softer, common-dialogue words that often appear in normal conversation live in
a separate opt-in file:

`profanity_words_optional_soft.csv`

They are **not** loaded by default. For stricter scene or romance filtering,
merge that file into `profanity_words.csv` (or append its entries).

## Frequently Asked Questions

### Is this really free?
**Yes.** It is free and open source, with no subscription required.

### Do I need Netflix or Amazon Prime?
**No.** It works with any video file you can save locally—downloads, rips, or files you already have.

### How long does processing take?
A 2-hour movie typically takes about 6–10 hours on CPU (base model with dialog enhancement) or about 20–40 minutes with a compatible GPU. Process once, then watch offline as often as you like. GPU rental can help for batch jobs.

### Will it work on my computer?
If you can run Python, yes. It works on Windows, macOS, and Linux. Minimum: 4GB RAM and a dual-core CPU.

### Is my privacy protected?
Yes. Everything runs locally on your computer—no cloud uploads, tracking, or data collection.

### Can I use this for YouTube videos?
Yes. Download with yt-dlp, then clean the video.

### Does it remove all profanity?
It matches transcribed speech against an editable word list (1,000+ default
entries) using the base model + dialog enhancement. Accuracy is high on clear
dialogue; some edge cases may still need manual review.

### Can I customize what gets filtered?
Yes. Edit `profanity_words.csv` to add, remove, or comment out words (prefix a
token with `#` to ignore it). Changes apply on the next run. Use
`--include-religious` for the optional religious/exclamatory list. For
stricter romance/scene filtering, merge entries from
`profanity_words_optional_soft.csv`. See
[Customize Filtered Words (CSV)](#customize-filtered-words-csv).

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

## Support & Community

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Share tips and ask questions
- **Contributions**: Pull requests welcome!
- **Star this repo**: Helps others find the project

---

## License

Open source and free to use. See LICENSE file for details.

---

## Contributing

Contributions welcome! Please open an issue or pull request on GitHub.
