#!/usr/bin/env python3
"""
Generate summary of what was cleaned from videos
"""

import sys
from pathlib import Path
import subprocess
from datetime import timedelta


def format_time(seconds: float) -> str:
    """Format seconds as MM:SS"""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def get_video_duration(video_path: Path) -> float:
    """Get video duration in seconds"""
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except:
        return 0.0


def analyze_cleaned_video(original_path: Path, cleaned_path: Path) -> dict:
    """Analyze what was removed by comparing original and cleaned videos"""
    if not cleaned_path.exists():
        return None
    
    original_duration = get_video_duration(original_path)
    cleaned_duration = get_video_duration(cleaned_path)
    time_removed = original_duration - cleaned_duration
    
    return {
        'original_duration': original_duration,
        'cleaned_duration': cleaned_duration,
        'time_removed': time_removed,
        'percentage_removed': (time_removed / original_duration * 100) if original_duration > 0 else 0
    }


def find_cleaned_videos(input_dir: Path, output_dir: Path) -> list:
    """Find all cleaned videos and their originals"""
    videos = []
    
    # Find all cleaned videos
    for cleaned_file in output_dir.glob('*_cleaned.mp4'):
        # Try to find original
        original_name = cleaned_file.stem.replace('_cleaned', '')
        
        # Search for original in input directory
        original_path = None
        for ext in ['.mp4', '.mkv', '.mov', '.avi']:
            potential = input_dir / f"{original_name}{ext}"
            if potential.exists():
                original_path = potential
                break
        
        if original_path:
            videos.append({
                'name': original_name,
                'original': original_path,
                'cleaned': cleaned_file,
                'cleaned_srt': output_dir / f"{cleaned_file.stem}.srt"
            })
    
    return videos


def generate_summary(input_dir: Path, output_dir: Path):
    """Generate summary report"""
    print("=" * 70)
    print("CLEANING SUMMARY REPORT")
    print("=" * 70)
    print()
    
    videos = find_cleaned_videos(input_dir, output_dir)
    
    if not videos:
        print(f"No cleaned videos found in {output_dir}")
        print("Make sure videos have been processed first.")
        return
    
    print(f"Found {len(videos)} cleaned video(s)\n")
    
    total_original_time = 0.0
    total_cleaned_time = 0.0
    total_removed_time = 0.0
    
    for i, video in enumerate(videos, 1):
        print(f"[{i}] {video['name']}")
        print("-" * 70)
        
        analysis = analyze_cleaned_video(video['original'], video['cleaned'])
        
        if analysis:
            original_dur = analysis['original_duration']
            cleaned_dur = analysis['cleaned_duration']
            removed = analysis['time_removed']
            pct = analysis['percentage_removed']
            
            print(f"  Original duration:  {format_time(original_dur)} ({original_dur:.1f}s)")
            print(f"  Cleaned duration:   {format_time(cleaned_dur)} ({cleaned_dur:.1f}s)")
            print(f"  Time removed:       {format_time(removed)} ({removed:.1f}s)")
            print(f"  Percentage removed: {pct:.1f}%")
            
            total_original_time += original_dur
            total_cleaned_time += cleaned_dur
            total_removed_time += removed
        else:
            print(f"  ⚠ Could not analyze video")
        
        # Check for subtitle file
        if video['cleaned_srt'].exists():
            print(f"  ✓ Subtitles cleaned: {video['cleaned_srt'].name}")
        else:
            print(f"  - No subtitles found")
        
        print()
    
    # Overall summary
    print("=" * 70)
    print("OVERALL SUMMARY")
    print("=" * 70)
    print(f"Total videos processed:     {len(videos)}")
    print(f"Total original duration:   {format_time(total_original_time)} ({total_original_time:.1f}s)")
    print(f"Total cleaned duration:    {format_time(total_cleaned_time)} ({total_cleaned_time:.1f}s)")
    print(f"Total time removed:        {format_time(total_removed_time)} ({total_removed_time:.1f}s)")
    if total_original_time > 0:
        overall_pct = (total_removed_time / total_original_time) * 100
        print(f"Overall percentage removed: {overall_pct:.1f}%")
    print()
    print(f"Cleaned videos location: {output_dir}")
    print("=" * 70)


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_summary.py <input_dir> <output_dir>")
        print("Example: python generate_summary.py test_videos_input test_videos_input/cleaned")
        sys.exit(1)
    
    input_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        sys.exit(1)
    
    if not output_dir.exists():
        print(f"Error: Output directory not found: {output_dir}")
        sys.exit(1)
    
    generate_summary(input_dir, output_dir)


if __name__ == '__main__':
    main()





