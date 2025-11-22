"""
Timestamp Merger - Merges video and audio segments into unified removal timeline
"""

from typing import List, Tuple


class TimestampMerger:
    """Merges segments from different sources into unified timeline"""
    
    def merge(self, video_segments: List[Tuple[float, float]], 
              audio_segments: List[Tuple[float, float, str]]) -> List[Tuple[float, float]]:
        """
        Merge video and audio segments.
        
        Args:
            video_segments: List of (start, end) tuples from video detection
            audio_segments: List of (start, end, word) tuples from audio detection OR (start, end) tuples
            
        Returns:
            Merged list of (start, end) tuples
        """
        # Convert audio segments to (start, end) format
        # Handle both (start, end, word) and (start, end) formats
        audio_only = []
        for seg in audio_segments:
            if len(seg) == 3:
                # Audio segment with word: (start, end, word)
                audio_only.append((seg[0], seg[1]))
            elif len(seg) == 2:
                # Already in (start, end) format
                audio_only.append((seg[0], seg[1]))
            else:
                # Invalid format - skip
                print(f"  Warning: Invalid segment format: {seg}")
        
        # Combine all segments
        all_segments = list(video_segments) + audio_only
        
        if not all_segments:
            return []
        
        # Validate segments
        valid_segments = []
        for start, end in all_segments:
            if start < 0 or end < 0:
                print(f"  Warning: Invalid segment with negative time: ({start}, {end})")
                continue
            if start >= end:
                print(f"  Warning: Invalid segment (start >= end): ({start}, {end})")
                continue
            valid_segments.append((start, end))
        
        if not valid_segments:
            return []
        
        # Sort by start time
        valid_segments.sort(key=lambda x: x[0])
        
        # Merge overlapping and nearby segments
        merged = []
        current_start, current_end = valid_segments[0]
        
        for start, end in valid_segments[1:]:
            # Merge if overlapping or within 0.5 seconds (scene continuity)
            if start <= current_end + 0.5:
                current_end = max(current_end, end)
            else:
                merged.append((current_start, current_end))
                current_start, current_end = start, end
        
        merged.append((current_start, current_end))
        
        return merged

