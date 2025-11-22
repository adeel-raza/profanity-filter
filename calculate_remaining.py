#!/usr/bin/env python3
"""Calculate how much video remains after removing segments"""

segments_to_remove = [
    (0, 26),      # 00:00 - 00:26
    (28, 63),     # 00:28 - 01:03
    (68, 173),    # 01:08 - 02:53
    (185, 189),   # 03:05 - 03:09
]

# Get video duration
import subprocess
from pathlib import Path

video_path = Path("./test_vidoes/8) Movie CLIP - Why Don't You Want to Have Sex_ (2005) HD.mp4")
cmd = [
    'ffprobe', '-v', 'error',
    '-show_entries', 'format=duration',
    '-of', 'default=noprint_wrappers=1:nokey=1',
    str(video_path)
]
result = subprocess.run(cmd, capture_output=True, text=True, check=True)
total_duration = float(result.stdout.strip())

# Calculate total removed time
total_removed = 0
for start, end in segments_to_remove:
    duration = end - start
    total_removed += duration

remaining = total_duration - total_removed
remaining_percent = (remaining / total_duration) * 100

def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

print("=" * 60)
print("VIDEO REMAINING CALCULATION")
print("=" * 60)
print(f"Total video duration: {format_time(total_duration)} ({total_duration:.1f}s)")
print(f"Time to remove: {format_time(total_removed)} ({total_removed:.1f}s)")
print(f"Time remaining: {format_time(remaining)} ({remaining:.1f}s)")
print(f"Percentage remaining: {remaining_percent:.1f}%")
print("=" * 60)




