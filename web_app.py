#!/usr/bin/env python3
"""
Web interface for Video Profanity Filter
Deploy to SiteGround or any Python hosting
"""

from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import os
import uuid
from pathlib import Path
import subprocess
import threading
import time
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'mkv', 'avi', 'mov', 'webm'}

# Create directories
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path(app.config['OUTPUT_FOLDER']).mkdir(exist_ok=True)
Path('static').mkdir(exist_ok=True)
Path('templates').mkdir(exist_ok=True)

# Store processing status
processing_status = {}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def process_video(video_path, output_path, session_id, whisper_model='tiny'):
    """Process video in background thread"""
    try:
        processing_status[session_id] = {
            'status': 'processing',
            'progress': 0,
            'message': 'Starting video processing...',
            'video_path': None,
            'subtitle_path': None
        }
        
        # Import here to avoid circular imports
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Run clean.py as subprocess
        cmd = [
            'python3',
            'clean.py',
            str(video_path),
            str(output_path),
            '--whisper-model', whisper_model
        ]
        
        processing_status[session_id]['message'] = 'Processing video...'
        processing_status[session_id]['progress'] = 10
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode == 0:
            # Check if output files exist
            video_output = output_path
            subtitle_output = output_path.parent / f"{output_path.stem}.srt"
            
            processing_status[session_id] = {
                'status': 'completed',
                'progress': 100,
                'message': 'Processing complete!',
                'video_path': str(video_output) if video_output.exists() else None,
                'subtitle_path': str(subtitle_output) if subtitle_output.exists() else None,
                'output': result.stdout
            }
        else:
            processing_status[session_id] = {
                'status': 'error',
                'progress': 0,
                'message': f'Error: {result.stderr}',
                'video_path': None,
                'subtitle_path': None
            }
    except Exception as e:
        processing_status[session_id] = {
            'status': 'error',
            'progress': 0,
            'message': f'Error: {str(e)}',
            'video_path': None,
            'subtitle_path': None
        }


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'video' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: MP4, MKV, AVI, MOV, WEBM'}), 400
    
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_filename = f"{timestamp}_{filename}"
    video_path = Path(app.config['UPLOAD_FOLDER']) / safe_filename
    file.save(str(video_path))
    
    # Generate output path
    output_path = Path(app.config['OUTPUT_FOLDER']) / f"{video_path.stem}_cleaned{video_path.suffix}"
    
    # Get whisper model from request
    whisper_model = request.form.get('whisper_model', 'tiny')
    
    # Start processing in background thread
    thread = threading.Thread(
        target=process_video,
        args=(video_path, output_path, session_id, whisper_model)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'session_id': session_id,
        'message': 'File uploaded and processing started'
    })


@app.route('/api/status/<session_id>')
def get_status(session_id):
    """Get processing status"""
    if session_id not in processing_status:
        return jsonify({'error': 'Session not found'}), 404
    
    status = processing_status[session_id]
    return jsonify(status)


@app.route('/api/download/<session_id>/<file_type>')
def download_file(session_id, file_type):
    """Download processed files"""
    if session_id not in processing_status:
        return jsonify({'error': 'Session not found'}), 404
    
    status = processing_status[session_id]
    
    if file_type == 'video':
        file_path = status.get('video_path')
    elif file_type == 'subtitle':
        file_path = status.get('subtitle_path')
    else:
        return jsonify({'error': 'Invalid file type'}), 400
    
    if not file_path or not Path(file_path).exists():
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(file_path, as_attachment=True)


@app.route('/api/cleanup/<session_id>', methods=['POST'])
def cleanup(session_id):
    """Clean up files after download"""
    try:
        if session_id in processing_status:
            status = processing_status[session_id]
            # Remove files
            for file_type in ['video_path', 'subtitle_path']:
                file_path = status.get(file_type)
                if file_path and Path(file_path).exists():
                    Path(file_path).unlink()
            # Remove status
            del processing_status[session_id]
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

