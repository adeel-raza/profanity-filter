#!/usr/bin/env python3
"""
Clean movies with verbose output and live progress tracking
"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
import threading
import queue


class ProgressTracker:
    """Track and display progress"""
    
    def __init__(self, total_videos):
        self.total_videos = total_videos
        self.current_video = 0
        self.start_time = None
        self.video_start_time = None
        self.video_times = []
        self.current_video_name = ""
        self.current_step = ""
        self.lock = threading.Lock()
    
    def start(self):
        self.start_time = time.time()
        print("=" * 80)
        print("MOVIE CLEANING - VERBOSE MODE WITH PROGRESS TRACKING")
        print("=" * 80)
        print(f"Total videos to process: {self.total_videos}")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
    
    def start_video(self, video_name):
        with self.lock:
            self.current_video += 1
            self.current_video_name = video_name
            self.video_start_time = time.time()
            self.current_step = "Initializing"
            # Print header for this video
            print(f"\n{'='*80}")
            print(f"PROCESSING VIDEO {self.current_video}/{self.total_videos}: {video_name}")
            print(f"{'='*80}")
    
    def update_step(self, step):
        with self.lock:
            self.current_step = step
            self._print_status()
    
    def finish_video(self, success=True):
        with self.lock:
            if self.video_start_time:
                elapsed = time.time() - self.video_start_time
                self.video_times.append(elapsed)
                status = "✓ SUCCESS" if success else "✗ FAILED"
                print(f"\n{'='*80}")
                print(f"VIDEO {self.current_video}/{self.total_videos} COMPLETE: {status}")
                print(f"Time taken: {elapsed/60:.1f} minutes ({self._format_time(elapsed)})")
                self._print_summary()
                print(f"{'='*80}\n")
            self.video_start_time = None
    
    def _print_status(self):
        # Don't print status line - let the actual output show instead
        # This prevents overwriting the verbose output
        pass
    
    def _print_summary(self):
        if self.video_times:
            avg_time = sum(self.video_times) / len(self.video_times)
            remaining = self.total_videos - self.current_video
            estimated = avg_time * remaining
            
            print(f"  Average time per video: {avg_time/60:.1f} min")
            if remaining > 0:
                print(f"  Estimated time remaining: {self._format_time(estimated)}")
            print()
    
    def _format_time(self, seconds):
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds//60)}m {int(seconds%60)}s"
        else:
            hours = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            return f"{hours}h {mins}m"
    
    def finish_all(self):
        total_time = time.time() - self.start_time if self.start_time else 0
        print()
        print("=" * 80)
        print("PROCESSING COMPLETE")
        print("=" * 80)
        print(f"Total time: {self._format_time(total_time)}")
        print(f"Average time per video: {sum(self.video_times)/len(self.video_times)/60:.1f} min" if self.video_times else "N/A")
        print("=" * 80)


def parse_output_line(line, tracker):
    """Parse output line and update tracker"""
    line_lower = line.lower()
    
    if "step 1:" in line_lower or "detecting profanity" in line_lower:
        tracker.update_step("Detecting audio profanity")
    elif "step 2:" in line_lower or "merging" in line_lower:
        tracker.update_step("Merging segments")
    elif "step 3:" in line_lower or "cutting out segments" in line_lower:
        tracker.update_step("Cutting video segments")
    elif "step 4:" in line_lower or "processing subtitles" in line_lower:
        tracker.update_step("Processing subtitles")
    elif "success" in line_lower:
        tracker.update_step("Completed")
    elif "analyzing" in line_lower and "frames" in line_lower:
        # Extract frame count if possible
        import re
        match = re.search(r'(\d+)\s*frames', line_lower)
        if match:
            tracker.update_step(f"Analyzing {match.group(1)} frames")
    elif "processing with ffmpeg" in line_lower:
        tracker.update_step("FFmpeg processing")


def process_movie(video_path, output_path, subtitle_path, tracker, script_dir):
    """Process a single movie with progress tracking"""
    tracker.start_video(video_path.name)
    print()  # New line after status
    
    cmd = [
        sys.executable,
        str(script_dir / 'clean.py'),
        str(video_path),
        str(output_path),
    ]
    
    if subtitle_path and subtitle_path.exists():
        cmd.extend(['--subs', str(subtitle_path)])
    
    try:
        # Use unbuffered output and run directly to show all output
        import os
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=0,  # Unbuffered
            universal_newlines=True,
            env=env
        )
        
        # Read and display ALL output in real-time
        import sys as sys_module
        
        # Read output line by line in real-time
        while True:
            output = process.stdout.readline()
            if not output and process.poll() is not None:
                break
            if output:
                line = output.rstrip('\n\r')
                # Print ALL lines immediately (this is verbose mode)
                print(line, flush=True)
                # Update tracker based on content
                parse_output_line(line, tracker)
        
        process.wait()
        success = process.returncode == 0
        
        # Print final status
        print()
        tracker.finish_video(success)
        return success
        
    except Exception as e:
        print(f"\n  Error: {e}")
        import traceback
        traceback.print_exc()
        tracker.finish_video(False)
        return False


def main():
    base_dir = Path("/home/adeel/Link to html/wp_local/movie_cleaner")
    script_dir = base_dir
    output_dir = base_dir / "movies" / "cleaned"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    movies = [
        {
            'name': 'Code_3',
            'input': base_dir / "movies" / "Code_3.mkv",
            'output': output_dir / "Code_3_cleaned.mkv",
            'subs': base_dir / "movies" / "Code_3.srt"
        },
        {
            'name': 'argo',
            'input': base_dir / "movies" / "argo" / "argo.mp4",
            'output': output_dir / "argo_cleaned.mp4",
            'subs': base_dir / "movies" / "argo" / "argo.srt"
        }
    ]
    
    # Filter out movies that don't exist
    movies = [m for m in movies if m['input'].exists()]
    
    if not movies:
        print("No movies found to process!")
        return
    
    tracker = ProgressTracker(len(movies))
    tracker.start()
    
    results = []
    for movie in movies:
        success = process_movie(
            movie['input'],
            movie['output'],
            movie['subs'],
            tracker,
            script_dir
        )
        results.append((movie['name'], success))
        print()  # Blank line between videos
    
    tracker.finish_all()
    
    # Generate summary
    print("\nGenerating summary...")
    summary_cmd = [
        sys.executable,
        str(base_dir / 'generate_summary.py'),
        str(base_dir / "movies"),
        str(output_dir)
    ]
    try:
        subprocess.run(summary_cmd, check=True)
    except Exception as e:
        print(f"Error generating summary: {e}")


if __name__ == '__main__':
    main()

