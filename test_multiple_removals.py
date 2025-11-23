#!/usr/bin/env python3
"""Test timestamp adjustment with multiple removed segments"""

# Test case: Remove segments 10-15 and 20-25
# Original subtitle at 30-35 should become 20-25 (shifted back by 10 seconds total)
# Original subtitle at 5-8 should stay 5-8 (before removals)
# Original subtitle at 12-18 should become 7-10 (overlaps first removal, clipped and adjusted)

removed_segments = [(10.0, 15.0), (20.0, 25.0)]

test_entries = [
    {'start': 5.0, 'end': 8.0, 'text': 'Before removals'},
    {'start': 12.0, 'end': 18.0, 'text': 'Overlaps first removal'},
    {'start': 30.0, 'end': 35.0, 'text': 'After both removals'},
]

print("Test case: Remove segments 10-15 and 20-25")
print("=" * 60)

sorted_removed = sorted(removed_segments, key=lambda x: x[0])

for entry in test_entries:
    entry_start = entry['start']
    entry_end = entry['end']
    
    # Calculate time removed before entry_start
    time_removed_before = 0.0
    for remove_start, remove_end in sorted_removed:
        if remove_end <= entry_start:
            time_removed_before += (remove_end - remove_start)
        elif remove_start < entry_start:
            time_removed_before += (entry_start - remove_start)
    
    # Calculate time removed within entry
    time_removed_in_entry = 0.0
    for remove_start, remove_end in sorted_removed:
        if entry_start < remove_end and entry_end > remove_start:
            overlap_start = max(entry_start, remove_start)
            overlap_end = min(entry_end, remove_end)
            time_removed_in_entry += (overlap_end - overlap_start)
    
    new_start = entry_start - time_removed_before
    new_end = entry_end - time_removed_before - time_removed_in_entry
    
    print(f"Original: {entry_start:.1f}-{entry_end:.1f} → Adjusted: {new_start:.1f}-{new_end:.1f}")
    print(f"  Time removed before: {time_removed_before:.1f}s")
    print(f"  Time removed in entry: {time_removed_in_entry:.1f}s")
    print()

