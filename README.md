# 🎬 Movie Profanity Filter

**Automated AI-powered tool to remove profanity, curse words, and obscene language from videos and subtitles - making movies family-friendly.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Whisper](https://img.shields.io/badge/Powered%20by-OpenAI%20Whisper-orange.svg)](https://github.com/openai/whisper)

## 🌟 Features

- ✅ **AI-Powered Audio Transcription** - Uses OpenAI Whisper for accurate speech-to-text
- ✅ **Comprehensive Profanity Detection** - 1,100+ curse words, sexual terms, and obscene language
- ✅ **Automatic Video Editing** - Cuts out profanity segments from video files
- ✅ **Subtitle Cleaning** - Removes profanity words from SRT/VTT subtitle files
- ✅ **Timestamp Synchronization** - Automatically adjusts subtitles after video cuts
- ✅ **Batch Processing** - Process multiple videos at once
- ✅ **CPU-Only** - Works without GPU, optimized for CPU processing
- ✅ **Fast Processing** - No video frame analysis, only audio transcription

## 📋 What It Does

This tool automatically:

1. **Transcribes audio** from your video using Whisper AI
2. **Detects profanity** in the transcribed text (1,100+ words)
3. **Cuts out profanity segments** from the video file
4. **Cleans subtitles** by removing profanity words
5. **Synchronizes subtitles** with the edited video

**Result:** A clean, family-friendly version of your movie with profanity removed from both audio and subtitles.

## 🚀 Quick Start

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
# Clean a single video with subtitles
python clean.py input.mp4 output.mp4 --subs input.srt

# Auto-detect subtitle file (if same name as video)
python clean.py movie.mp4 cleaned_movie.mp4

# Process without subtitles (audio only)
python clean.py video.mp4 cleaned_video.mp4
```

## 📖 Detailed Usage

### Command Line Options

```bash
python clean.py [input_video] [output_video] [options]

Options:
  --subs SUBTITLE_FILE    Input subtitle file (SRT or VTT)
  --whisper-model MODEL   Whisper model size (tiny, base, small, medium, large)
                          Default: tiny (fastest, good accuracy)
  --no-audio              Skip audio profanity detection
  --remove-timestamps     Manually specify timestamps to remove
                          Format: "start-end,start-end" (e.g., "10-15,30-35")
```

### Examples

#### Example 1: Basic Video Cleaning
```bash
python clean.py sample/fyou.mp4 sample/cleaned/fyou_cleaned.mp4 --subs sample/fyou.srt
```

**Output:**
- ✅ Detected 22 profanity segments
- ✅ Removed 25.42 seconds of profanity
- ✅ Cleaned video: `fyou_cleaned.mp4`
- ✅ Cleaned subtitles: `fyou_cleaned.srt`

#### Example 2: Using Larger Whisper Model (Better Accuracy)
```bash
python clean.py movie.mp4 cleaned.mp4 --subs movie.srt --whisper-model base
```

#### Example 3: Batch Processing Multiple Videos
```bash
python batch_process.py input_folder/ output_folder/
```

## 🎯 What Gets Filtered

The tool filters **1,132 profanity words** including:

- **Curse Words**: fuck, shit, damn, hell, ass, bitch, bastard, etc.
- **Sexual Terms**: sex, porn, nude, orgasm, masturbation, etc.
- **Body Parts**: penis, vagina, breast, etc.
- **Abusive Language**: whore, slut, cunt, etc.
- **Obscene Terms**: Various vulgar and offensive language

**Note:** "Damn" and variations are **NOT** filtered (not considered obscene for family viewing).

## ⚡ Performance

### Processing Speed

For a **2-hour movie**:
- **Audio Extraction**: ~30 seconds
- **Whisper Transcription** (tiny model): ~5-10 minutes
- **Video Cutting**: ~2-5 minutes (if profanity found)
- **Total Time**: ~7-15 minutes

**Much faster than video-based NSFW detection** (which would take 30-60 minutes for the same movie).

### System Requirements

- **OS**: Linux, macOS, or Windows
- **Python**: 3.8 or higher
- **RAM**: 2-4 GB minimum
- **Storage**: ~2 GB for models and dependencies
- **CPU**: Any modern CPU (GPU optional, not required)

## 📁 Project Structure

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

## 🔧 Advanced Usage

### Generate Subtitles (If You Don't Have Them)

```bash
python generate_subtitles.py video.mp4 output.srt --model tiny
```

### Process Multiple Videos

```bash
python batch_process.py /path/to/videos/ /path/to/output/ --whisper-model tiny
```

### Manual Timestamp Removal

```bash
python clean.py video.mp4 cleaned.mp4 --remove-timestamps "10-15,30-35,60-65"
```

## 🛠️ How It Works

1. **Audio Extraction**: Extracts audio track from video using FFmpeg
2. **Transcription**: Uses OpenAI Whisper to transcribe audio with word-level timestamps
3. **Profanity Detection**: Matches transcribed words against 1,132-word profanity list
4. **Segment Merging**: Merges nearby profanity segments (within 1 second)
5. **Video Cutting**: Uses FFmpeg to cut out profanity segments
6. **Subtitle Processing**: Removes profanity words from subtitles and adjusts timestamps

## 📊 Example Output

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

## 🎓 Use Cases

- **Family Movie Nights** - Make any movie suitable for children
- **Content Creators** - Clean videos for broader audience
- **Educational Content** - Remove inappropriate language
- **Public Screenings** - Ensure content is appropriate
- **Personal Libraries** - Maintain family-friendly video collections

## 🔒 Privacy & Security

- ✅ **100% Local Processing** - All processing happens on your machine
- ✅ **No Internet Required** - Works completely offline after installation
- ✅ **No Data Upload** - Your videos never leave your computer
- ✅ **Open Source** - Full transparency, inspect the code yourself

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Areas for Contribution

- Add more profanity words to the list
- Improve word matching accuracy (reduce false positives)
- Add support for more video formats
- Optimize processing speed
- Add more subtitle formats

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenAI Whisper** - For accurate speech-to-text transcription
- **FFmpeg** - For video/audio processing
- **Python Community** - For excellent libraries

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/adeel-raza/profanity-filter/issues)
- **Discussions**: [GitHub Discussions](https://github.com/adeel-raza/profanity-filter/discussions)

## ⭐ Star History

If you find this tool useful, please consider giving it a ⭐ on GitHub!

---

**Made with ❤️ for creating family-friendly content**
