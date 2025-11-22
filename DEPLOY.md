# Quick Deploy Guide

## Option 1: Deploy via Hugging Face Website (Easiest)

1. **Go to**: https://huggingface.co/spaces
2. **Click**: "Create new Space"
3. **Fill in**:
   - **Space name**: `movie-profanity-filter`
   - **SDK**: Select **Gradio**
   - **Hardware**: Select **CPU basic** (free tier)
   - **Visibility**: Public
4. **Click**: "Create Space"

5. **Upload files** (drag and drop or use Git):
   - `app.py`
   - `gradio_app.py`
   - `clean.py`
   - `audio_profanity_detector.py`
   - `subtitle_processor.py`
   - `video_cutter.py`
   - `timestamp_merger.py`
   - `profanity_words.py`
   - `requirements_hf.txt` (rename to `requirements.txt` in the Space)
   - `README.md` (optional)

6. **Wait**: Hugging Face will automatically build and deploy (5-10 minutes)

7. **Done**: Your app will be live at:
   `https://huggingface.co/spaces/YOUR_USERNAME/movie-profanity-filter`

## Option 2: Deploy via Git (Recommended)

If you want to connect your GitHub repo:

1. **Push this repo to GitHub** (already done)

2. **In Hugging Face Space**:
   - Go to your Space settings
   - Click "Repository" tab
   - Click "Connect to GitHub"
   - Select your repository: `adeel-raza/profanity-filter`
   - Select branch: `main`
   - Set root directory: `/` (root)
   - Click "Connect"

3. **Hugging Face will auto-deploy** from GitHub

## Option 3: Use Hugging Face CLI

```bash
# Install Hugging Face CLI
pip install huggingface_hub

# Login
huggingface-cli login

# Create space
huggingface-cli repo create movie-profanity-filter --type space --space-sdk gradio

# Clone the space
git clone https://huggingface.co/spaces/YOUR_USERNAME/movie-profanity-filter
cd movie-profanity-filter

# Copy files
cp ../movie_cleaner/app.py .
cp ../movie_cleaner/gradio_app.py .
cp ../movie_cleaner/clean.py .
cp ../movie_cleaner/audio_profanity_detector.py .
cp ../movie_cleaner/subtitle_processor.py .
cp ../movie_cleaner/video_cutter.py .
cp ../movie_cleaner/timestamp_merger.py .
cp ../movie_cleaner/profanity_words.py .
cp ../movie_cleaner/requirements_hf.txt requirements.txt

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

## File Checklist

Make sure these files are in your Space:
- [x] `app.py` (required entry point)
- [x] `gradio_app.py` (Gradio interface)
- [x] `clean.py` (main script)
- [x] `audio_profanity_detector.py`
- [x] `subtitle_processor.py`
- [x] `video_cutter.py`
- [x] `timestamp_merger.py`
- [x] `profanity_words.py`
- [x] `requirements.txt` (from requirements_hf.txt)

## Troubleshooting

**Build fails?**
- Check that `requirements.txt` exists (not `requirements_hf.txt`)
- Ensure `app.py` is in the root directory
- Check build logs in Space settings

**App crashes?**
- Check logs in Space settings
- Verify FFmpeg is available (should be pre-installed)
- Ensure all Python files are uploaded

**Slow processing?**
- Use `tiny` Whisper model
- Consider upgrading to paid tier for better performance

