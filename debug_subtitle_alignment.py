#!/usr/bin/env python3
"""Debug subtitle alignment by comparing original and cleaned"""

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
        print(f"Error: {e}")
        return None

def parse_srt_time(time_str: str) -> float:
    """Convert SRT time format to seconds"""
    time_str = time_str.strip()
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
    milliseconds = int(ms_part[:3])
    
    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0

def parse_srt_file(srt_path: Path) -> list:
    """Parse SRT file"""
    entries = []
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    blocks = re.split(r'\n\s*\n', content.strip())
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        
        try:
            index = int(lines[0])
        except:
            continue
        
        time_line = lines[1]
        if '-->' not in time_line:
            continue
        
        start_str, end_str = time_line.split('-->')
        start = parse_srt_time(start_str.strip())
        end = parse_srt_time(end_str.strip())
        text = '\n'.join(lines[2:]).strip()
        
        entries.append({
            'index': index,
            'start': start,
            'end': end,
            'text': text
        })
    
    return entries

def debug_alignment(original_srt: Path, cleaned_srt: Path, original_video: Path, cleaned_video: Path):
    """Debug subtitle alignment"""
    print("=" * 70)
    print("DEBUGGING SUBTITLE ALIGNMENT")
    print("=" * 70)
    
    orig_duration = get_video_duration(original_video)
    cleaned_duration = get_video_duration(cleaned_video)
    
    print(f"\nOriginal video: {orig_duration:.2f}s")
    print(f"Cleaned video: {cleaned_duration:.2f}s")
    print(f"Time removed: {orig_duration - cleaned_duration:.2f}s")
    
    orig_entries = parse_srt_file(original_srt)
    cleaned_entries = parse_srt_file(cleaned_srt)
    
    print(f"\nOriginal subtitles: {len(orig_entries)} entries")
    print(f"Cleaned subtitles: {len(cleaned_entries)} entries")
    
    # Compare first 10 entries
    print("\n" + "-" * 70)
    print("First 10 entries comparison:")
    print("-" * 70)
    print(f"{'Index':<6} {'Original Start':<15} {'Cleaned Start':<15} {'Diff':<10} {'Text':<40}")
    print("-" * 70)
    
    for i in range(min(10, len(orig_entries), len(cleaned_entries))):
        orig = orig_entries[i]
        cleaned = cleaned_entries[i] if i < len(cleaned_entries) else None
        
        if cleaned:
            diff = cleaned['start'] - orig['start']
            print(f"{orig['index']:<6} {orig['start']:>13.2f}s  {cleaned['start']:>13.2f}s  {diff:>8.2f}s  {orig['text'][:38]}")
        else:
            print(f"{orig['index']:<6} {orig['start']:>13.2f}s  {'MISSING':<15} {'N/A':<10}  {orig['text'][:38]}")
    
    # Check if cleaned video duration matches last subtitle
    if cleaned_entries:
        last_entry = cleaned_entries[-1]
        print(f"\nLast subtitle ends at: {last_entry['end']:.2f}s")
        print(f"Cleaned video duration: {cleaned_duration:.2f}s")
        print(f"Difference: {cleaned_duration - last_entry['end']:.2f}s")
        
        if abs(cleaned_duration - last_entry['end']) > 5.0:
            print("⚠ WARNING: Last subtitle doesn't match video end!")
        else:
            print("✓ Last subtitle aligns with video end")

if __name__ == "__main__":
    base_dir = Path("sample")
    original_srt = base_dir / "fyou.srt"
    cleaned_srt = base_dir / "fyou_cleaned.srt"
    original_video = base_dir / "fyou.mp4"
    cleaned_video = base_dir / "fyou_cleaned.mp4"
    
    if all(f.exists() for f in [original_srt, cleaned_srt, original_video, cleaned_video]):
        debug_alignment(original_srt, cleaned_srt, original_video, cleaned_video)
    else:
        print("ERROR: Files not found")
        for f in [original_srt, cleaned_srt, original_video, cleaned_video]:
            print(f"  {f.name}: {f.exists()}")

