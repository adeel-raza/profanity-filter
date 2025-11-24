# Deploying Video Profanity Filter to SiteGround

## Prerequisites

1. SiteGround hosting account with Python support
2. SSH access enabled (contact SiteGround support)
3. Python 3.8+ installed on server

## Deployment Steps

### 1. Upload Files

Upload all project files to your SiteGround public_html directory (or subdirectory):

```
public_html/
├── web_app.py
├── clean.py
├── audio_profanity_detector.py
├── subtitle_processor.py
├── video_cutter.py
├── timestamp_merger.py
├── profanity_words.py
├── generate_subtitles.py
├── requirements_web.txt
├── .htaccess
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
├── uploads/ (create empty directory)
└── outputs/ (create empty directory)
```

### 2. Set Permissions

Via SSH or File Manager, set permissions:
```bash
chmod 755 web_app.py
chmod 755 clean.py
chmod 755 *.py
chmod 777 uploads/
chmod 777 outputs/
```

### 3. Install Dependencies

SSH into your SiteGround server and install Python dependencies:

```bash
cd ~/public_html  # or your directory
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_web.txt
```

**Note**: PyTorch and Whisper are large. If installation fails due to space, contact SiteGround support or use a VPS.

### 4. Install FFmpeg

Contact SiteGround support to install FFmpeg, or install via SSH if you have root access:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg

# Or ask SiteGround support to install it
```

### 5. Configure .htaccess

The `.htaccess` file is already configured. Ensure it's in your root directory.

### 6. Test the Application

1. Visit your domain: `https://yourdomain.com/web_app.py`
2. Or if using mod_wsgi: `https://yourdomain.com/`

### 7. Set Up Cron Job (Optional)

For cleanup of old files, add a cron job:

```bash
# Clean files older than 24 hours
0 * * * * find /path/to/uploads -type f -mtime +1 -delete
0 * * * * find /path/to/outputs -type f -mtime +1 -delete
```

## Alternative: Using Python Anywhere or Heroku

If SiteGround doesn't support Python apps well, consider:

### Python Anywhere
- Free tier available
- Python pre-installed
- Easy Flask deployment

### Heroku
- Free tier (limited)
- Easy deployment with Git
- Automatic scaling

## Troubleshooting

### Issue: "Module not found"
**Solution**: Ensure virtual environment is activated and dependencies are installed

### Issue: "FFmpeg not found"
**Solution**: Contact SiteGround support to install FFmpeg

### Issue: "Permission denied"
**Solution**: Check file permissions (755 for scripts, 777 for upload/output directories)

### Issue: "File too large"
**Solution**: Adjust `MAX_CONTENT_LENGTH` in `web_app.py` or contact support

## Security Notes

1. **File Cleanup**: Files are automatically deleted after download, but set up cron job for safety
2. **Rate Limiting**: Consider adding rate limiting for production
3. **HTTPS**: Ensure SSL certificate is installed
4. **Input Validation**: Already implemented, but review for your needs

## Performance Optimization

1. **Use CDN**: Serve static files (CSS/JS) from CDN
2. **Caching**: Add caching headers for static content
3. **Queue System**: For high traffic, consider Celery for background processing
4. **Database**: Store session info in database instead of memory for multi-server setup

## Support

For issues:
1. Check SiteGround Python documentation
2. Contact SiteGround support for server-specific issues
3. Review Flask deployment guides

