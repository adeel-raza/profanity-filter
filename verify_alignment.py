#!/usr/bin/env python3
"""Verify subtitle alignment with cleaned video"""

import subprocess
from pathlib import Path
import re

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
    except Exception as e:
        print(f"Error getting video duration: {e}")
        return None

def parse_srt_time(time_str: str) -> float:
    """Convert SRT time format (HH:MM:SS,mmm) to seconds"""
    time_str = time_str.strip()
    # Handle both comma and period as millisecond separator
    if ',' in time_str:
        time_part, ms_part = time_str.split(',')
    elif '.' in time_str:
        time_part, ms_part = time_str.split('.')
    else:
        time_part = time_str
        ms_part = "000"
    
    parts = time_part.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = int(parts[2])
    milliseconds = int(ms_part[:3])  # Take first 3 digits
    
    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0

def parse_srt_file(srt_path: Path) -> list:
    """Parse SRT file and return list of subtitle entries"""
    entries = []
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by double newlines (entry separator)
    blocks = re.split(r'\n\s*\n', content.strip())
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        
        # Parse index
        try:
            index = int(lines[0])
        except:
            continue
        
        # Parse time
        time_line = lines[1]
        if '-->' not in time_line:
            continue
        
        start_str, end_str = time_line.split('-->')
        start = parse_srt_time(start_str.strip())
        end = parse_srt_time(end_str.strip())
        
        # Parse text
        text = '\n'.join(lines[2:]).strip()
        
        entries.append({
            'index': index,
            'start': start,
            'end': end,
            'text': text
        })
    
    return entries

def verify_alignment(original_srt: Path, cleaned_srt: Path, cleaned_video: Path, removed_segments: list):
    """Verify that cleaned subtitles align with cleaned video"""
    print("=" * 70)
    print("SUBTITLE ALIGNMENT VERIFICATION")
    print("=" * 70)
    
    # Get video duration
    video_duration = get_video_duration(cleaned_video)
    if video_duration:
        print(f"\nCleaned video duration: {video_duration:.2f} seconds ({video_duration/60:.2f} minutes)")
    
    # Parse subtitle files
    original_entries = parse_srt_file(original_srt)
    cleaned_entries = parse_srt_file(cleaned_srt)
    
    print(f"\nOriginal subtitles: {len(original_entries)} entries")
    print(f"Cleaned subtitles: {len(cleaned_entries)} entries")
    print(f"Removed segments: {len(removed_segments)}")
    
    # Check if cleaned subtitles are within video duration
    print("\n" + "-" * 70)
    print("CHECK 1: Subtitle timestamps within video duration")
    print("-" * 70)
    
    out_of_range = []
    for entry in cleaned_entries:
        if entry['start'] > video_duration + 1.0:  # Allow 1 second tolerance
            out_of_range.append(entry)
        if entry['end'] > video_duration + 1.0:
            out_of_range.append(entry)
    
    if out_of_range:
        print(f"⚠️  WARNING: {len(out_of_range)} entries extend beyond video duration!")
        for entry in out_of_range[:5]:
            print(f"    Entry {entry['index']}: {entry['start']:.2f}s - {entry['end']:.2f}s")
    else:
        print("✓ All subtitle timestamps are within video duration")
    
    # Check first and last entries
    print("\n" + "-" * 70)
    print("CHECK 2: First and last subtitle entries")
    print("-" * 70)
    
    if cleaned_entries:
        first = cleaned_entries[0]
        last = cleaned_entries[-1]
        print(f"First entry: {first['start']:.2f}s - {first['end']:.2f}s")
        print(f"  Text: {first['text'][:60]}...")
        print(f"Last entry: {last['start']:.2f}s - {last['end']:.2f}s")
        print(f"  Text: {last['text'][:60]}...")
        print(f"Video duration: {video_duration:.2f}s")
        
        if last['end'] > video_duration + 2.0:
            print(f"⚠️  WARNING: Last subtitle ends at {last['end']:.2f}s but video is {video_duration:.2f}s")
        else:
            print("✓ Last subtitle aligns with video end")
    
    # Check sample entries for alignment
    print("\n" + "-" * 70)
    print("CHECK 3: Sample subtitle entries (every 10%)")
    print("-" * 70)
    
    if cleaned_entries:
        sample_indices = [int(len(cleaned_entries) * i / 10) for i in range(0, 11)]
        for idx in sample_indices:
            if idx < len(cleaned_entries):
                entry = cleaned_entries[idx]
                percentage = (entry['start'] / video_duration * 100) if video_duration else 0
                print(f"Entry {entry['index']}: {entry['start']:.2f}s - {entry['end']:.2f}s ({percentage:.1f}% of video)")
                print(f"  Text: {entry['text'][:50]}...")
    
    print("\n" + "=" * 70)
    print("Verification complete!")
    print("=" * 70)

if __name__ == "__main__":
    # Test with The Gambler
    base_dir = Path("movies/The Gambler (2014) [1080p]")
    original_srt = base_dir / "The.Gambler.2014.1080p.BluRay.x264.YIFY.srt"
    cleaned_srt = base_dir / "The.Gambler.2014.1080p.BluRay.x264.YIFY_cleaned.srt"
    cleaned_video = base_dir / "The.Gambler.2014.1080p.BluRay.x264.YIFY_cleaned.mp4"
    
    # We don't have removed_segments here, but we can still verify alignment
    if cleaned_video.exists() and cleaned_srt.exists():
        verify_alignment(original_srt, cleaned_srt, cleaned_video, [])
    else:
        print(f"Files not found:")
        print(f"  Video: {cleaned_video.exists()}")
        print(f"  SRT: {cleaned_srt.exists()}")

