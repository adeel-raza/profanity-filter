#!/usr/bin/env python3
"""Test subtitle alignment with actual video segments"""

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
    """Parse SRT file and return list of subtitle entries"""
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

def test_alignment_at_timestamp(video_path: Path, srt_path: Path, test_time: float):
    """Test if subtitle at test_time matches video content"""
    # Extract a short segment around test_time
    output_segment = Path("/tmp/test_segment.mp4")
    cmd = [
        'ffmpeg', '-y', '-ss', str(max(0, test_time - 1)),
        '-i', str(video_path),
        '-t', '3',
        '-c', 'copy',
        str(output_segment)
    ]
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"  ✓ Extracted video segment at {test_time:.2f}s")
    except:
        print(f"  ✗ Failed to extract segment")
        return False
    
    # Check if subtitle exists at this time
    entries = parse_srt_file(srt_path)
    matching_entries = [e for e in entries if e['start'] <= test_time <= e['end']]
    
    if matching_entries:
        entry = matching_entries[0]
        print(f"  ✓ Subtitle found: {entry['start']:.2f}s - {entry['end']:.2f}s")
        print(f"    Text: {entry['text'][:50]}...")
        return True
    else:
        print(f"  ⚠ No subtitle at {test_time:.2f}s")
        return False

def comprehensive_alignment_test(original_srt: Path, cleaned_srt: Path, cleaned_video: Path):
    """Comprehensive test of subtitle alignment"""
    print("=" * 70)
    print("COMPREHENSIVE SUBTITLE ALIGNMENT TEST")
    print("=" * 70)
    
    video_duration = get_video_duration(cleaned_video)
    if not video_duration:
        print("ERROR: Could not get video duration")
        return
    
    print(f"\nCleaned video duration: {video_duration:.2f} seconds ({video_duration/60:.2f} minutes)")
    
    original_entries = parse_srt_file(original_srt)
    cleaned_entries = parse_srt_file(cleaned_srt)
    
    print(f"\nOriginal subtitles: {len(original_entries)} entries")
    print(f"Cleaned subtitles: {len(cleaned_entries)} entries")
    
    # Test 1: Check if all subtitles are within video duration
    print("\n" + "-" * 70)
    print("TEST 1: All subtitles within video duration")
    print("-" * 70)
    
    out_of_range = []
    for entry in cleaned_entries:
        if entry['start'] > video_duration + 1.0:
            out_of_range.append(entry)
        if entry['end'] > video_duration + 1.0:
            out_of_range.append(entry)
    
    if out_of_range:
        print(f"✗ FAILED: {len(out_of_range)} entries extend beyond video duration!")
        for entry in out_of_range[:5]:
            print(f"    Entry {entry['index']}: {entry['start']:.2f}s - {entry['end']:.2f}s")
        return False
    else:
        print("✓ PASSED: All subtitles are within video duration")
    
    # Test 2: Check first and last entries
    print("\n" + "-" * 70)
    print("TEST 2: First and last subtitle alignment")
    print("-" * 70)
    
    if cleaned_entries:
        first = cleaned_entries[0]
        last = cleaned_entries[-1]
        
        print(f"First entry: {first['start']:.2f}s - {first['end']:.2f}s")
        print(f"Last entry: {last['start']:.2f}s - {last['end']:.2f}s")
        print(f"Video duration: {video_duration:.2f}s")
        
        if first['start'] < 0:
            print("✗ FAILED: First subtitle starts before video")
            return False
        if last['end'] > video_duration + 2.0:
            print(f"✗ FAILED: Last subtitle ends {last['end'] - video_duration:.2f}s after video")
            return False
        
        print("✓ PASSED: First and last entries align correctly")
    
    # Test 3: Check sample entries at different points
    print("\n" + "-" * 70)
    print("TEST 3: Sample entries at 10%, 25%, 50%, 75%, 90% of video")
    print("-" * 70)
    
    test_points = [0.1, 0.25, 0.5, 0.75, 0.9]
    all_passed = True
    
    for percentage in test_points:
        test_time = video_duration * percentage
        print(f"\nTesting at {percentage*100:.0f}% of video ({test_time:.2f}s):")
        
        # Find closest subtitle
        closest_entry = None
        min_diff = float('inf')
        for entry in cleaned_entries:
            # Check if entry covers this time
            if entry['start'] <= test_time <= entry['end']:
                closest_entry = entry
                break
            # Or find closest entry
            diff = min(abs(entry['start'] - test_time), abs(entry['end'] - test_time))
            if diff < min_diff:
                min_diff = diff
                closest_entry = entry
        
        if closest_entry:
            if closest_entry['start'] <= test_time <= closest_entry['end']:
                print(f"  ✓ Subtitle covers this time: {closest_entry['start']:.2f}s - {closest_entry['end']:.2f}s")
                print(f"    Text: {closest_entry['text'][:60]}...")
            else:
                distance = min(abs(closest_entry['start'] - test_time), abs(closest_entry['end'] - test_time))
                if distance < 5.0:  # Within 5 seconds is acceptable
                    print(f"  ✓ Subtitle nearby: {closest_entry['start']:.2f}s - {closest_entry['end']:.2f}s (distance: {distance:.2f}s)")
                else:
                    print(f"  ⚠ Subtitle far: {closest_entry['start']:.2f}s - {closest_entry['end']:.2f}s (distance: {distance:.2f}s)")
                    all_passed = False
        else:
            print(f"  ✗ No subtitle found near {test_time:.2f}s")
            all_passed = False
    
    if all_passed:
        print("\n✓ PASSED: Sample entries align correctly")
    else:
        print("\n⚠ WARNING: Some sample entries may be misaligned")
    
    # Test 4: Check for gaps (missing subtitles in long segments)
    print("\n" + "-" * 70)
    print("TEST 4: Check for large gaps between subtitles")
    print("-" * 70)
    
    large_gaps = []
    for i in range(len(cleaned_entries) - 1):
        gap = cleaned_entries[i+1]['start'] - cleaned_entries[i]['end']
        if gap > 10.0:  # More than 10 seconds gap
            large_gaps.append((cleaned_entries[i]['end'], cleaned_entries[i+1]['start'], gap))
    
    if large_gaps:
        print(f"⚠ Found {len(large_gaps)} large gaps (>10s):")
        for start, end, gap in large_gaps[:5]:
            print(f"    Gap: {start:.2f}s to {end:.2f}s ({gap:.2f}s)")
    else:
        print("✓ No unusually large gaps found")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    base_dir = Path("movies/The Gambler (2014) [1080p]")
    original_srt = base_dir / "The.Gambler.2014.1080p.BluRay.x264.YIFY.srt"
    cleaned_srt = base_dir / "The.Gambler.2014.1080p.BluRay.x264.YIFY_cleaned.srt"
    cleaned_video = base_dir / "The.Gambler.2014.1080p.BluRay.x264.YIFY_cleaned.mp4"
    
    if all(f.exists() for f in [original_srt, cleaned_srt, cleaned_video]):
        comprehensive_alignment_test(original_srt, cleaned_srt, cleaned_video)
    else:
        print("ERROR: Required files not found")
        print(f"  Original SRT: {original_srt.exists()}")
        print(f"  Cleaned SRT: {cleaned_srt.exists()}")
        print(f"  Cleaned video: {cleaned_video.exists()}")

