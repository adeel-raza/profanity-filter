# Movie Cleaner - Quick Commands

## Generic Command to Clean Any Movie

### Simple Method (Recommended)
```bash
cd "/home/adeel/Link to html/wp_local/movie_cleaner"
./clean_movie.sh <path_to_video_file>
```

**Examples:**
```bash
./clean_movie.sh movies/Code_3.mkv
./clean_movie.sh movies/argo/argo.mp4
./clean_movie.sh /full/path/to/movie.mp4
```

### What It Does:
- ✅ Auto-detects subtitle file (same name + `.srt` in same folder)
- ✅ Creates cleaned video in `<folder>/cleaned/` directory
- ✅ Shows **ALL output in real-time** (verbose mode)
- ✅ Uses fast detector (NudeNet + Hugging Face)
- ✅ Processes and aligns subtitles automatically

### Direct Python Command (Alternative)
```bash
cd "/home/adeel/Link to html/wp_local/movie_cleaner"
source venv/bin/activate
PYTHONUNBUFFERED=1 python clean.py <input_video> <output_video> \
    --fast --nsfw-threshold 0.3 --sample-rate 0.5 \
    --subs <subtitle_file>
```

## Verbose Output

The command shows **real-time progress** including:
- Step 1: Detecting explicit content in video
  - Frame extraction progress
  - NudeNet detection results
  - Hugging Face model analysis
  - Found segments with timestamps
- Step 2: Detecting profanity in audio
  - Whisper transcription progress
  - Profanity detection results
- Step 3: Merging segments
- Step 4: Cutting video segments
  - FFmpeg processing
- Step 5: Processing subtitles
  - Subtitle filtering and alignment
- Final summary with statistics

## Subtitle Auto-Detection

The script automatically looks for subtitle files in this order:
1. `<video_name>.srt` (same folder as video)
2. `<video_name>.en.srt` (same folder as video)

If no subtitle file is found, the video is processed without subtitles.

## Output Location

Cleaned videos are saved to:
- `<video_folder>/cleaned/<video_name>_cleaned.<extension>`
- Subtitles: `<video_folder>/cleaned/<video_name>_cleaned.srt`

## Notes

- **No background processes** - runs directly in terminal
- **Real-time verbose output** - see everything as it happens
- **Large movies** (1-2GB) may take 30-60+ minutes
- Press `Ctrl+C` to cancel if needed





