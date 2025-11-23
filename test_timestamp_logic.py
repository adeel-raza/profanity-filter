#!/usr/bin/env python3
"""Test the timestamp adjustment logic with a simple example"""

# Test case: Remove segment 10-15 from a 100-second video
# Keep segments: (0, 10), (15, 100)
# Original video: 0-100s
# Cleaned video: 0-95s (removed 5 seconds)

removed_segments = [(10.0, 15.0)]

# Test entries
test_cases = [
    # (original_start, original_end, expected_cleaned_start, expected_cleaned_end, description)
    (5.0, 8.0, 5.0, 8.0, "Before removal - no change"),
    (12.0, 18.0, 12.0, 13.0, "Overlaps removal - should be clipped to 12-13 (before removal part)"),
    (20.0, 25.0, 15.0, 20.0, "After removal - shifted back by 5 seconds"),
    (8.0, 12.0, 8.0, 10.0, "Starts before, ends in removal - clipped to 8-10"),
    (14.0, 20.0, 14.0, 15.0, "Starts in removal, ends after - clipped to 14-15 (but wait, 14 is in removal!)"),
]

def get_time_removed_before(timestamp: float, removed_segments):
    """Current algorithm"""
    sorted_removed = sorted(removed_segments, key=lambda x: x[0])
    time_removed = 0.0
    for remove_start, remove_end in sorted_removed:
        if remove_end <= timestamp:
            time_removed += (remove_end - remove_start)
        elif remove_start < timestamp:
            time_removed += (timestamp - remove_start)
    return time_removed

print("Testing timestamp adjustment logic:")
print("=" * 70)
print("Removed segment: 10.0s - 15.0s (5 seconds)")
print("Keep segments: (0, 10), (15, 100)")
print("=" * 70)
print()

for orig_start, orig_end, expected_start, expected_end, desc in test_cases:
    # Simulate clipping (if entry overlaps removal)
    clipped_start = orig_start
    clipped_end = orig_end
    
    for remove_start, remove_end in removed_segments:
        if orig_start < remove_end and orig_end > remove_start:
            # Entry overlaps removal
            if orig_start < remove_start:
                # Entry starts before removal
                if orig_end > remove_end:
                    # Entry spans removal - we keep parts before and after
                    # But for simplicity, let's just keep the part before
                    clipped_end = remove_start
                else:
                    # Entry ends in removal - keep part before
                    clipped_end = remove_start
            elif orig_start >= remove_start:
                # Entry starts in or after removal
                if orig_end <= remove_end:
                    # Completely in removal - should be removed
                    clipped_start = None
                    break
                else:
                    # Starts in removal, ends after - keep part after
                    clipped_start = remove_end
    
    if clipped_start is None:
        print(f"Entry {orig_start:.1f}-{orig_end:.1f}: REMOVED (completely in removal)")
        continue
    
    # Adjust timestamps
    time_removed_before_start = get_time_removed_before(clipped_start, removed_segments)
    time_removed_before_end = get_time_removed_before(clipped_end, removed_segments)
    
    new_start = clipped_start - time_removed_before_start
    new_end = clipped_end - time_removed_before_end
    
    print(f"Entry {orig_start:.1f}-{orig_end:.1f}: {desc}")
    print(f"  Clipped to: {clipped_start:.1f}-{clipped_end:.1f}")
    print(f"  Time removed before start: {time_removed_before_start:.1f}s")
    print(f"  Time removed before end: {time_removed_before_end:.1f}s")
    print(f"  Adjusted to: {new_start:.1f}-{new_end:.1f}")
    print(f"  Expected: {expected_start:.1f}-{expected_end:.1f}")
    
    if abs(new_start - expected_start) < 0.1 and abs(new_end - expected_end) < 0.1:
        print(f"  ✓ CORRECT")
    else:
        print(f"  ✗ WRONG - Expected {expected_start:.1f}-{expected_end:.1f}, got {new_start:.1f}-{new_end:.1f}")
    print()

