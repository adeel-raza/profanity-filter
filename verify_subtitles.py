#!/usr/bin/env python3
"""
Verify that cleaned subtitles accurately match the filtered video
"""

import re
from pathlib import Path
from typing import List, Tuple


def parse_srt_timestamp(timestamp_str: str) -> float:
    """Convert SRT timestamp (HH:MM:SS,mmm) to seconds"""
    match = re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})', timestamp_str)
    if not match:
        return 0.0
    hours, minutes, seconds, milliseconds = map(int, match.groups())
    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0


def parse_srt_file(srt_path: Path) -> List[dict]:
    """Parse SRT file and return list of subtitle entries"""
    entries = []
    content = srt_path.read_text(encoding='utf-8')
    
    # Split by double newlines
    blocks = re.split(r'\n\s*\n', content.strip())
    
    for block in blocks:
        if not block.strip():
            continue
        
        lines = block.strip().split('\n')
        if len(lines) < 2:
            continue
        
        try:
            index = int(lines[0])
        except ValueError:
            continue
        
        # Parse timestamp line
        timestamp_line = lines[1]
        time_match = re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})', 
                             timestamp_line)
        if not time_match:
            continue
        
        start = parse_srt_timestamp(time_match.group(0).split(' --> ')[0])
        end = parse_srt_timestamp(time_match.group(0).split(' --> ')[1])
        text = '\n'.join(lines[2:]).strip()
        
        entries.append({
            'index': index,
            'start': start,
            'end': end,
            'text': text
        })
    
    return entries


def verify_subtitles(original_srt: Path, cleaned_srt: Path, removed_segments: List[Tuple[float, float]]):
    """
    Verify that cleaned subtitles accurately reflect removed segments
    """
    print("=" * 60)
    print("SUBTITLE VERIFICATION")
    print("=" * 60)
    
    original_entries = parse_srt_file(original_srt)
    cleaned_entries = parse_srt_file(cleaned_srt)
    
    print(f"\nOriginal subtitles: {len(original_entries)} entries")
    print(f"Cleaned subtitles: {len(cleaned_entries)} entries")
    print(f"Removed: {len(original_entries) - len(cleaned_entries)} entries")
    print(f"\nRemoved video segments: {len(removed_segments)}")
    for start, end in removed_segments:
        print(f"  - {start:.2f}s to {end:.2f}s")
    
    # Check 1: Entries in removed segments should be gone
    print("\n" + "-" * 60)
    print("CHECK 1: Entries overlapping removed segments")
    print("-" * 60)
    
    removed_entries = []
    for entry in original_entries:
        for remove_start, remove_end in removed_segments:
            # Check if entry overlaps with removed segment
            if entry['start'] < remove_end and entry['end'] > remove_start:
                removed_entries.append(entry)
                break
    
    print(f"Found {len(removed_entries)} original entries that overlap removed segments")
    
    # Verify these entries are NOT in cleaned file
    cleaned_starts = {e['start'] for e in cleaned_entries}
    still_present = [e for e in removed_entries if e['start'] in cleaned_starts]
    
    if still_present:
        print(f"⚠️  WARNING: {len(still_present)} entries that should be removed are still present!")
        for entry in still_present[:5]:
            print(f"    Entry {entry['index']}: {entry['start']:.2f}s - {entry['end']:.2f}s")
    else:
        print("✓ All entries overlapping removed segments were correctly removed")
    
    # Check 2: Timestamp adjustments
    print("\n" + "-" * 60)
    print("CHECK 2: Timestamp adjustments")
    print("-" * 60)
    
    # Calculate expected time removed before each original entry
    sorted_removed = sorted(removed_segments, key=lambda x: x[0])
    
    errors = []
    for orig_entry in original_entries:
        # Skip if this entry was removed
        if any(orig_entry['start'] < rem_end and orig_entry['end'] > rem_start 
               for rem_start, rem_end in removed_segments):
            continue
        
        # Find corresponding cleaned entry (by text or approximate time)
        expected_time_removed = sum(
            rem_end - rem_start 
            for rem_start, rem_end in sorted_removed 
            if rem_end <= orig_entry['start']
        )
        
        expected_start = orig_entry['start'] - expected_time_removed
        expected_end = orig_entry['end'] - expected_time_removed
        
        # Find matching cleaned entry
        matching_cleaned = None
        for cleaned_entry in cleaned_entries:
            # Match by text or close timestamp
            if (cleaned_entry['text'] == orig_entry['text'] or 
                abs(cleaned_entry['start'] - expected_start) < 1.0):
                matching_cleaned = cleaned_entry
                break
        
        if matching_cleaned:
            start_diff = abs(matching_cleaned['start'] - expected_start)
            end_diff = abs(matching_cleaned['end'] - expected_end)
            
            if start_diff > 0.1 or end_diff > 0.1:
                errors.append({
                    'original': orig_entry,
                    'cleaned': matching_cleaned,
                    'expected_start': expected_start,
                    'expected_end': expected_end,
                    'start_diff': start_diff,
                    'end_diff': end_diff
                })
    
    if errors:
        print(f"⚠️  WARNING: {len(errors)} entries have timestamp adjustment errors")
        for err in errors[:3]:
            print(f"    Entry {err['original']['index']}:")
            print(f"      Expected: {err['expected_start']:.2f}s - {err['expected_end']:.2f}s")
            print(f"      Actual: {err['cleaned']['start']:.2f}s - {err['cleaned']['end']:.2f}s")
            print(f"      Difference: {err['start_diff']:.2f}s / {err['end_diff']:.2f}s")
    else:
        print("✓ All timestamp adjustments are accurate")
    
    # Check 3: Sample comparison
    print("\n" + "-" * 60)
    print("CHECK 3: Sample comparison (first 5 entries)")
    print("-" * 60)
    
    print("\nOriginal subtitles (first 5):")
    for entry in original_entries[:5]:
        print(f"  {entry['index']}: {entry['start']:.2f}s - {entry['end']:.2f}s: {entry['text'][:50]}")
    
    print("\nCleaned subtitles (first 5):")
    for entry in cleaned_entries[:5]:
        print(f"  {entry['index']}: {entry['start']:.2f}s - {entry['end']:.2f}s: {entry['text'][:50]}")
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    if not still_present and not errors:
        print("✓ ALL CHECKS PASSED - Subtitles are accurately filtered and aligned!")
    else:
        print("⚠️  Some issues found - see details above")
    
    print(f"\nOriginal: {len(original_entries)} entries")
    print(f"Cleaned: {len(cleaned_entries)} entries")
    print(f"Removed: {len(removed_entries)} entries (overlapping removed segments)")


if __name__ == '__main__':
    import sys
    
    original_srt = Path(sys.argv[1])
    cleaned_srt = Path(sys.argv[2])
    
    # Removed segments from the processing output
    removed_segments = [
        (22.12, 23.00),
        (50.50, 55.00),
        (81.00, 89.72),
        (95.50, 100.00),
        (106.00, 118.00),
        (121.50, 129.50),
        (134.00, 160.50),
        (164.50, 169.00)
    ]
    
    verify_subtitles(original_srt, cleaned_srt, removed_segments)




