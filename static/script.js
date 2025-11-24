let currentSessionId = null;
let statusCheckInterval = null;

// File input handler
document.getElementById('videoInput').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        document.getElementById('fileName').textContent = `Selected: ${file.name} (${formatFileSize(file.size)})`;
        document.getElementById('optionsBox').style.display = 'block';
    }
});

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

async function processVideo() {
    const fileInput = document.getElementById('videoInput');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a video file first');
        return;
    }
    
    // Show progress section
    document.getElementById('progressSection').style.display = 'block';
    document.getElementById('uploadSection')?.style.setProperty('display', 'none');
    document.getElementById('resultsSection').style.display = 'none';
    
    // Create form data
    const formData = new FormData();
    formData.append('video', file);
    formData.append('whisper_model', document.getElementById('whisperModel').value);
    
    try {
        // Upload file
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }
        
        const data = await response.json();
        currentSessionId = data.session_id;
        
        // Start checking status
        checkStatus();
        
    } catch (error) {
        alert('Error: ' + error.message);
        resetForm();
    }
}

function checkStatus() {
    if (!currentSessionId) return;
    
    statusCheckInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/status/${currentSessionId}`);
            if (!response.ok) {
                throw new Error('Status check failed');
            }
            
            const status = await response.json();
            updateProgress(status);
            
            if (status.status === 'completed' || status.status === 'error') {
                clearInterval(statusCheckInterval);
                
                if (status.status === 'completed') {
                    showResults(status);
                } else {
                    alert('Error: ' + status.message);
                    resetForm();
                }
            }
        } catch (error) {
            console.error('Status check error:', error);
            clearInterval(statusCheckInterval);
            alert('Error checking status');
            resetForm();
        }
    }, 2000); // Check every 2 seconds
}

function updateProgress(status) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const progressDetails = document.getElementById('progressDetails');
    
    progressFill.style.width = status.progress + '%';
    progressText.textContent = status.message;
    
    if (status.output) {
        // Extract useful info from output
        const lines = status.output.split('\n');
        const lastLines = lines.slice(-5).join('\n');
        progressDetails.textContent = lastLines;
    }
}

function showResults(status) {
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';
    
    // Store file paths in data attributes
    const videoBtn = document.querySelector('[onclick="downloadFile(\'video\')"]');
    const subtitleBtn = document.querySelector('[onclick="downloadFile(\'subtitle\')"]');
    
    if (status.video_path) {
        videoBtn.disabled = false;
        videoBtn.dataset.path = status.video_path;
    } else {
        videoBtn.disabled = true;
    }
    
    if (status.subtitle_path) {
        subtitleBtn.disabled = false;
        subtitleBtn.dataset.path = status.subtitle_path;
    } else {
        subtitleBtn.disabled = true;
    }
}

async function downloadFile(fileType) {
    if (!currentSessionId) return;
    
    try {
        const response = await fetch(`/api/download/${currentSessionId}/${fileType}`);
        if (!response.ok) {
            throw new Error('Download failed');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileType === 'video' ? 'cleaned_video.mp4' : 'cleaned_subtitles.srt';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        // Clean up after download
        await fetch(`/api/cleanup/${currentSessionId}`, { method: 'POST' });
        
    } catch (error) {
        alert('Error downloading file: ' + error.message);
    }
}

function resetForm() {
    document.getElementById('videoInput').value = '';
    document.getElementById('fileName').textContent = '';
    document.getElementById('optionsBox').style.display = 'none';
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
    
    currentSessionId = null;
}

