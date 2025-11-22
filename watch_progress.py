#!/usr/bin/env python3
"""
Watch progress of movie cleaning in real-time
"""

import time
import subprocess
import sys
from pathlib import Path
import os

def get_video_duration(video_path):
    """Get video duration"""
    try:
        cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
               '-of', 'default=noprint_wrappers=1:nokey=1', str(video_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except:
        return 0

def format_time(seconds):
    """Format seconds"""
    if seconds == 0:
        return "N/A"
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def check_process_status():
    """Check what processes are running"""
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    
    code3_running = False
    argo_running = False
    
    for line in lines:
        if 'clean.py' in line and 'Code_3' in line:
            code3_running = True
            parts = line.split()
            if len(parts) > 2:
                cpu = parts[2]
                mem = parts[3]
                print(f"  Code_3: Running (CPU: {cpu}%, MEM: {mem}%)")
        if 'clean.py' in line and 'argo' in line:
            argo_running = True
            parts = line.split()
            if len(parts) > 2:
                cpu = parts[2]
                mem = parts[3]
                print(f"  argo: Running (CPU: {cpu}%, MEM: {mem}%)")
    
    return code3_running, argo_running

def main():
    base_dir = Path("/home/adeel/Link to html/wp_local/movie_cleaner")
    cleaned_dir = base_dir / "movies" / "cleaned"
    
    print("=" * 70)
    print("MOVIE CLEANING PROGRESS MONITOR")
    print("=" * 70)
    print()
    
    # Check output files
    code3_output = cleaned_dir / "Code_3_cleaned.mkv"
    argo_output = cleaned_dir / "argo_cleaned.mp4"
    
    print("=== OUTPUT FILES STATUS ===")
    if code3_output.exists():
        size = code3_output.stat().st_size / (1024*1024*1024)  # GB
        print(f"  Code_3_cleaned.mkv: EXISTS ({size:.2f} GB)")
        
        # Try to get duration to see if it's complete
        duration = get_video_duration(code3_output)
        if duration > 0:
            print(f"    Duration: {format_time(duration)}")
    else:
        print(f"  Code_3_cleaned.mkv: Not created yet")
    
    if argo_output.exists():
        size = argo_output.stat().st_size / (1024*1024*1024)  # GB
        print(f"  argo_cleaned.mp4: EXISTS ({size:.2f} GB)")
        duration = get_video_duration(argo_output)
        if duration > 0:
            print(f"    Duration: {format_time(duration)}")
    else:
        print(f"  argo_cleaned.mp4: Not created yet")
    
    print()
    print("=== PROCESS STATUS ===")
    code3_running, argo_running = check_process_status()
    
    if not code3_running and not argo_running:
        print("  No processes running - may have completed or not started")
    
    print()
    print("=== ESTIMATED PROGRESS ===")
    
    # Check original file sizes
    code3_original = base_dir / "movies" / "Code_3.mkv"
    argo_original = base_dir / "movies" / "argo" / "argo.mp4"
    
    if code3_original.exists():
        orig_size = code3_original.stat().st_size
        if code3_output.exists():
            out_size = code3_output.stat().st_size
            if out_size > 0:
                progress = min(100, (out_size / orig_size) * 100)
                print(f"  Code_3: ~{progress:.1f}% (based on file size)")
            else:
                print(f"  Code_3: Initializing...")
        else:
            print(f"  Code_3: Not started yet")
    
    if argo_original.exists():
        orig_size = argo_original.stat().st_size
        if argo_output.exists():
            out_size = argo_output.stat().st_size
            if out_size > 0:
                progress = min(100, (out_size / orig_size) * 100)
                print(f"  argo: ~{progress:.1f}% (based on file size)")
            else:
                print(f"  argo: Initializing...")
        else:
            print(f"  argo: Waiting for Code_3 to complete")
    
    print()
    print("=" * 70)
    print("Note: Large movies (1-2GB) can take 30-60+ minutes each")
    print("Check again in a few minutes for updated progress")
    print("=" * 70)

if __name__ == '__main__':
    main()




