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

**If you find this project helpful, please consider supporting it:**
[![Support via Stripe](https://img.shields.io/badge/Support%20via%20Stripe-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://link.elearningevolve.com/self-pay)

---

## Installation

### Prerequisites

Install these before cloning:

- **Python 3.8+** (with `pip` and venv support)
- **FFmpeg and FFprobe**
- **Git**
- Optional: NVIDIA CUDA for faster transcription / encoding

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install -y git python3 python3-pip python3-venv ffmpeg

# Fedora
sudo dnf install -y git python3 python3-pip ffmpeg

# macOS
brew install git python ffmpeg
```

On Windows: install [Python](https://www.python.org/downloads/) (enable PATH),
[Git](https://git-scm.com/download/win), and FFmpeg
(`winget install Gyan.FFmpeg` or add it to `PATH` manually).

### Setup

```bash
git clone https://github.com/adeel-raza/profanity-filter.git
cd profanity-filter
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 clean.py --help
```

On Ubuntu/Debian you can also run `./install.sh`.

### Docker (optional)

```bash
# CPU
docker build -t profanity-filter:cpu --target cpu .
docker run --rm -v "$PWD":/data -v profanity-hf-cache:/cache \
  profanity-filter:cpu /app/clean.py /data/input.mp4 /data/output.mp4

# GPU (needs NVIDIA Container Toolkit)
docker build -t profanity-filter:gpu --target gpu .
docker run --rm --gpus all -v "$PWD":/data -v profanity-hf-cache:/cache \
  profanity-filter:gpu /app/clean.py /data/input.mp4 /data/output.mp4
```

---

## Usage

Movie-length files can take a long time on CPU. A GPU helps a lot. Providing
subtitles is the biggest speed win when you already have them.

```bash
# Basic clean (writes cleaned video + .srt)
python3 clean.py movie.mp4 movie_cleaned.mp4

# Faster: use existing subtitles (also auto-detects movie.srt next to movie.mp4)
python3 clean.py movie.mp4 movie_cleaned.mp4 --subs movie.srt

# Mute swear words instead of cutting the timeline
python3 clean.py movie.mp4 movie_cleaned.mp4 --mute-only

# Optional religious / exclamatory terms
python3 clean.py movie.mp4 movie_cleaned.mp4 --include-religious

# YouTube download then clean
yt-dlp -o "video.%(ext)s" "https://www.youtube.com/watch?v=VIDEO_ID"
python3 clean.py video.mp4 video_cleaned.mp4
```

### Useful options

| Option | Purpose |
|--------|---------|
| `--subs FILE` | Use / point to an SRT or VTT file (faster) |
| `--mute-only` | Mute matched speech instead of cutting |
| `--include-religious` | Also filter religious/exclamatory terms |
| `--model SIZE` | `tiny`, `base`, `small`, `medium`, or `large` |
| `--hybrid` | Subtitle-first + selective audio (needs subtitles) |
| `--remove-timestamps "a-b,c-d"` | Manually remove extra ranges |
| `--dump-transcript FILE` | Save word-level transcript for review |
| `--no-dialog-enhance` | Disable speech audio preprocessing |
| `--no-auto-upgrade` | Don't retry with a larger model on weak transcripts |

Run `python3 clean.py --help` for the full list.

### Output

- `*_cleaned.mp4` (or your chosen output path) — cleaned video
- `*_cleaned.srt` — cleaned subtitles

---

## Customize Filtered Words (CSV)

Edit `profanity_words.csv` to control what gets filtered. Changes apply the next
time you run `clean.py` or restart the Gradio app.

1. Open `profanity_words.csv`.
2. Words/phrases are comma-separated and can span lines.
3. Delete words you never want filtered; add new ones in lowercase.
4. Prefix a token with `#` to comment it out.
5. Save, then run again.

```csv
word-one,word-two,phrase one
another-term
# notes-or-disabled-entry
```

An empty CSV disables the default list. If the file is missing, built-in
defaults are used.

Religious/exclamatory terms stay off unless you pass `--include-religious`.

For stricter scene/romance filtering, merge entries from
`profanity_words_optional_soft.csv` into `profanity_words.csv`. That soft list
is **not** loaded by default.

---

## FAQ

**Is it free?**  
Yes. Open source, no subscription.

**Do I need Netflix or another streaming service?**  
No. It works on local video files (and downloads you already have).

**How long does a movie take?**  
Often several hours on CPU; much faster with a GPU. Subtitles speed it up a lot.
Process once, then watch offline.

**Does it remove everything?**  
It matches transcribed speech against your word list. Clear dialogue works well;
edge cases may need `--remove-timestamps` or word-list edits.

**Can I customize the filter list?**  
Yes — edit `profanity_words.csv` (see above).

---

## Troubleshooting

**`faster-whisper` / import errors**

```bash
python3 -m pip install -r requirements.txt
```

**FFmpeg not found**

```bash
# Ubuntu/Debian
sudo apt install -y ffmpeg
# macOS
brew install ffmpeg
# Windows
winget install Gyan.FFmpeg
```

Then reopen the terminal and check `ffmpeg -version`.

**Very slow on CPU**  
Expected for long videos. Use `--subs`, a GPU if you have one, or a smaller
`--model` (faster, but may miss more).

**Missed words**  
Try `--dump-transcript words.txt`, a larger `--model`, or add timestamps with
`--remove-timestamps`.

---

## License

Open source. See the `LICENSE` file for details.

## Contributing

Issues and pull requests are welcome on GitHub.
