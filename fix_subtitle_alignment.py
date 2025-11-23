#!/usr/bin/env python3
"""Fix subtitle alignment by matching video cutter's exact logic"""

# The video cutter keeps segments: (0, r1_start), (r1_end, r2_start), ..., (rN_end, video_end)
# We need to map original timestamps to cleaned video timestamps

def calculate_keep_segments(removed_segments, video_duration):
    """Calculate keep segments exactly like video cutter"""
    if not removed_segments:
        return [(0.0, video_duration)]
    
    sorted_removed = sorted(removed_segments, key=lambda x: x[0])
    keep_segments = []
    current_time = 0.0
    
    for remove_start, remove_end in sorted_removed:
        if current_time < remove_start:
            keep_segments.append((current_time, remove_start))
        current_time = max(current_time, remove_end)
    
    if current_time < video_duration:
        keep_segments.append((current_time, video_duration))
    
    return keep_segments

def map_timestamp_to_cleaned(original_time, keep_segments_original, removed_segments):
    """Map original timestamp to cleaned video timestamp"""
    # Find which keep segment this timestamp is in
    for keep_start, keep_end in keep_segments_original:
        if keep_start <= original_time < keep_end:
            # Calculate position within this keep segment
            position_in_segment = original_time - keep_start
            
            # Calculate where this keep segment starts in cleaned video
            # Sum all removals that happened before this keep segment
            time_removed_before = 0.0
            for remove_start, remove_end in removed_segments:
                if remove_end <= keep_start:
                    time_removed_before += (remove_end - remove_start)
            
            # In cleaned video, this keep segment starts at (keep_start - time_removed_before)
            cleaned_start = keep_start - time_removed_before
            
            # Map the timestamp
            return cleaned_start + position_in_segment
    
    # If timestamp is at or after last keep segment end, handle it
    if keep_segments_original:
        last_keep_start, last_keep_end = keep_segments_original[-1]
        if original_time >= last_keep_end:
            # Calculate total removed time
            total_removed = sum(end - start for start, end in removed_segments)
            return original_time - total_removed
    
    return original_time

# Test with example
removed = [(10.0, 15.0)]
video_duration = 100.0

keep_segments = calculate_keep_segments(removed, video_duration)
print("Keep segments:", keep_segments)
print()

test_times = [5.0, 12.0, 20.0, 50.0]
for orig_time in test_times:
    cleaned_time = map_timestamp_to_cleaned(orig_time, keep_segments, removed)
    print(f"Original {orig_time:.1f}s → Cleaned {cleaned_time:.1f}s")

