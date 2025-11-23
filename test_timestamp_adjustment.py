#!/usr/bin/env python3
"""Test timestamp adjustment logic"""

# Test case: Remove segment 10-15 from video
# Original subtitle at 20-25 should become 15-20 (shifted back by 5 seconds)
# Original subtitle at 5-8 should stay 5-8 (before removal)
# Original subtitle at 12-18 should become 12-13 (clipped, only keep part before removal)

removed_segments = [(10.0, 15.0)]

test_entries = [
    {'start': 5.0, 'end': 8.0, 'text': 'Before removal'},
    {'start': 12.0, 'end': 18.0, 'text': 'Overlaps removal'},
    {'start': 20.0, 'end': 25.0, 'text': 'After removal'},
]

# Expected results:
# Entry 1: 5.0-8.0 → 5.0-8.0 (no change, before removal)
# Entry 2: 12.0-18.0 → 12.0-13.0 (clipped to part before removal, then adjusted)
# Entry 3: 20.0-25.0 → 15.0-20.0 (shifted back by 5 seconds)

print("Test case: Remove segment 10-15")
print("=" * 60)
for entry in test_entries:
    entry_start = entry['start']
    entry_end = entry['end']
    
    # Calculate time removed before entry_start
    time_removed_before = 0.0
    for remove_start, remove_end in removed_segments:
        if remove_end <= entry_start:
            time_removed_before += (remove_end - remove_start)
        elif remove_start < entry_start:
            time_removed_before += (entry_start - remove_start)
    
    # Calculate time removed within entry
    time_removed_in_entry = 0.0
    for remove_start, remove_end in removed_segments:
        if entry_start < remove_end and entry_end > remove_start:
            # Entry overlaps with removal
            overlap_start = max(entry_start, remove_start)
            overlap_end = min(entry_end, remove_end)
            time_removed_in_entry += (overlap_end - overlap_start)
    
    new_start = entry_start - time_removed_before
    new_end = entry_end - time_removed_before - time_removed_in_entry
    
    print(f"Original: {entry_start:.1f}-{entry_end:.1f} → Adjusted: {new_start:.1f}-{new_end:.1f}")
    print(f"  Time removed before: {time_removed_before:.1f}s")
    print(f"  Time removed in entry: {time_removed_in_entry:.1f}s")

