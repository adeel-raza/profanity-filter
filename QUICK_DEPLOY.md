# Quick Deploy - 3 Steps

## Step 1: Login to Hugging Face

```bash
huggingface-cli login
```

Enter your Hugging Face token when prompted.
(Get token from: https://huggingface.co/settings/tokens)

## Step 2: Run Auto-Deploy Script

```bash
python3 auto_deploy.py
```

This will:
- Create the Space (if it doesn't exist)
- Upload all necessary files
- Configure everything automatically

## Step 3: Wait for Build

- Go to: https://huggingface.co/spaces/YOUR_USERNAME/video-profanity-filter
- Wait 5-10 minutes for first build
- Your app will be live!

---

## Alternative: Manual Deploy

If auto-deploy doesn't work:

1. **Create Space**: https://huggingface.co/spaces → "Create new Space"
   - Name: `video-profanity-filter`
   - SDK: `Gradio`
   - Hardware: `CPU basic`

2. **Upload Files** (via web interface or Git):
   - `app.py`
   - `gradio_app.py`
   - `clean.py`
   - `audio_profanity_detector.py`
   - `subtitle_processor.py`
   - `video_cutter.py`
   - `timestamp_merger.py`
   - `profanity_words.py`
   - `requirements_hf.txt` → rename to `requirements.txt`

3. **Wait for deployment** (5-10 minutes)

Done!
