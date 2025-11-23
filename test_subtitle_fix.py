#!/usr/bin/env python3
"""Test subtitle filtering and adjustment"""

from pathlib import Path
from subtitle_processor import SubtitleProcessor

# Test with actual segments
removed_segments = [
    (6.0, 11.0),
    (22.12, 30.0),
    (50.0, 60.0),
    (87.64, 89.72),
    (136.48, 137.38),
    (139.5, 143.5),
    (148.2, 150.18)
]

input_srt = Path("./test_vidoes/8) Movie CLIP - Why Don't You Want to Have Sex_ (2005) HD.srt")
output_srt = Path("./test_vidoes/test_cleaned_subtitles.srt")

processor = SubtitleProcessor()

# Read and parse
with open(input_srt, 'r', encoding='utf-8') as f:
    content = f.read()

entries = processor._parse_srt(content)
print(f"Original entries: {len(entries)}")
print(f"First 5 entries:")
for e in entries[:5]:
    print(f"  {e['start']:.3f}-{e['end']:.3f}: {e['text'][:50]}")

# Filter
filtered = processor._filter_entries(entries, removed_segments)
print(f"\nFiltered entries: {len(filtered)}")
print(f"Removed: {len(entries) - len(filtered)} entries")

# Check if entries in removed segments are gone
for entry in filtered:
    entry_start = entry['start']
    entry_end = entry['end']
    for rs, re in removed_segments:
        if entry_start < re and entry_end > rs:
            print(f"ERROR: Entry {entry_start:.3f}-{entry_end:.3f} overlaps with removed {rs}-{re}!")

# Adjust
adjusted = processor._adjust_timestamps(filtered, removed_segments)
print(f"\nAdjusted entries: {len(adjusted)}")
print(f"First 5 adjusted entries:")
for e in adjusted[:5]:
    print(f"  {e['start']:.3f}-{e['end']:.3f}: {e['text'][:50]}")

# Write
processor._write_srt(output_srt, adjusted)
print(f"\nTest output written to: {output_srt}")





