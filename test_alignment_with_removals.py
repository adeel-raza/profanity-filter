#!/usr/bin/env python3
"""Test alignment with actual removed segments"""

from subtitle_processor import SubtitleProcessor
from pathlib import Path

# Test with The Gambler which has profanity
processor = SubtitleProcessor()
srt_path = Path('movies/The Gambler (2014) [1080p]/The.Gambler.2014.1080p.BluRay.x264.YIFY.srt')
cleaned_srt = Path('movies/The Gambler (2014) [1080p]/The.Gambler.2014.1080p.BluRay.x264.YIFY_cleaned.srt')

if not srt_path.exists():
    print("Original SRT not found")
    exit(1)

# Read original
with open(srt_path, 'r', encoding='utf-8') as f:
    content = f.read()

orig_entries = processor._parse_srt(content)

# Simulate removed segments (from actual processing)
# First removal is around 80s
removed_segments = [(80.48, 82.47), (526.68, 528.91)]

print("Testing alignment with removed segments:")
print(f"Removed: {removed_segments}")
print()

# Find entries before, during, and after first removal
test_entries = []
for entry in orig_entries:
    if entry['start'] < 80:  # Before removal
        test_entries.append(("Before removal", entry))
        break

for entry in orig_entries:
    if 80 <= entry['start'] < 85:  # Around removal
        test_entries.append(("Around removal", entry))
        break

for entry in orig_entries:
    if entry['start'] > 530:  # After removal
        test_entries.append(("After removal", entry))
        break

print("Testing entry adjustment:")
for label, entry in test_entries:
    print(f"\n{label}:")
    print(f"  Original: {entry['start']:.2f}s - {entry['end']:.2f}s")
    
    # Clip if needed
    clipped = processor._clip_entry_to_keep_segments(entry, removed_segments)
    if clipped:
        print(f"  After clipping: {clipped[0]['start']:.2f}s - {clipped[0]['end']:.2f}s")
        # Adjust
        adjusted = processor._adjust_timestamps(clipped, removed_segments)
        if adjusted:
            print(f"  After adjustment: {adjusted[0]['start']:.2f}s - {adjusted[0]['end']:.2f}s")
            print(f"  Text: {adjusted[0]['text'][:50]}...")
    else:
        print(f"  Entry removed (completely in removal)")

