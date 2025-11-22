# Deploying to Hugging Face Spaces

This guide will help you deploy the Movie Profanity Filter to Hugging Face Spaces for free hosting.

## Quick Deploy

1. **Create a Hugging Face account** (if you don't have one)
   - Go to https://huggingface.co/join
   - Sign up for free

2. **Create a new Space**
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Name it (e.g., `video-profanity-filter`)
   - Select **Gradio** as the SDK
   - Select **Python** as the hardware
   - Click "Create Space"

3. **Upload files to your Space**
   - Clone this repository
   - Upload all Python files to your Space:
     - `app.py` (entry point)
     - `gradio_app.py` (Gradio interface)
     - `clean.py` (main cleaning script)
     - `audio_profanity_detector.py`
     - `subtitle_processor.py`
     - `video_cutter.py`
     - `timestamp_merger.py`
     - `profanity_words.py`
     - `requirements_hf.txt` (rename to `requirements.txt` in the Space)
   - Upload `README.md` (optional, for Space description)

4. **Configure the Space**
   - In your Space settings, make sure:
     - SDK is set to **Gradio**
     - Python version is **3.10** or higher
     - Hardware is **CPU basic** (free tier)

5. **Deploy**
   - Hugging Face will automatically build and deploy
   - Wait for the build to complete (5-10 minutes first time)
   - Your app will be live at: `https://huggingface.co/spaces/YOUR_USERNAME/video-profanity-filter`

## File Structure in Hugging Face Space

```
your-space/
├── app.py                    # Entry point (required)
├── gradio_app.py            # Gradio interface
├── clean.py                 # Main cleaning script
├── audio_profanity_detector.py
├── subtitle_processor.py
├── video_cutter.py
├── timestamp_merger.py
├── profanity_words.py
├── requirements.txt         # Dependencies (rename from requirements_hf.txt)
└── README.md               # Space description (optional)
```

## Important Notes

### File Size Limits
- **Maximum file size**: 5 GB per upload
- Videos larger than 5 GB cannot be processed
- Consider compressing videos before upload

### Processing Time Limits
- **Free tier**: 60 seconds timeout
- **CPU basic**: 5 minutes timeout
- For longer videos, users may need to upgrade to paid tier

### Resource Limits
- **Free tier**: Limited CPU and RAM
- Processing may be slower than local installation
- Consider using `tiny` Whisper model for faster processing

### Storage
- Files are stored temporarily during processing
- Cleaned files are available for download
- Files are automatically deleted after a period of inactivity

## Troubleshooting

### Build Fails
- Check that `requirements.txt` is correctly named
- Ensure all Python files are uploaded
- Check build logs in Space settings

### App Crashes
- Check logs in Space settings
- Ensure FFmpeg is available (it should be pre-installed)
- Verify all dependencies are in `requirements.txt`

### Slow Processing
- Use `tiny` Whisper model for faster processing
- Consider upgrading to paid tier for better performance
- Large videos will take longer to process

## Updating Your Space

1. Make changes to files locally
2. Upload updated files to your Space
3. Hugging Face will automatically rebuild and redeploy

## Sharing Your Space

Once deployed, you can share your Space URL with anyone:
```
https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
```

Users can:
- Upload videos directly in the browser
- Process videos without installing anything
- Download cleaned videos and subtitles

## Alternative: Use GitHub Integration

1. Push this repository to GitHub
2. In Hugging Face Space settings, connect to GitHub
3. Select your repository
4. Hugging Face will auto-deploy from GitHub

This way, you can update the Space by pushing to GitHub!

