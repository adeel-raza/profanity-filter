"""
Subtitle Processor - Removes subtitle segments matching video cuts and adjusts timestamps
"""

import re
from pathlib import Path
from typing import List, Tuple, Optional

from profanity_words import PROFANITY_WORDS


class SubtitleProcessor:
    """Processes subtitles to align with cut video and filter profanity"""
    
    # Use shared profanity word list
    PROFANITY_WORDS = PROFANITY_WORDS
    
    def process_srt(self, input_srt: Path, output_srt: Path, 
                    removed_segments: List[Tuple[float, float]]) -> bool:
        """
        Process SRT subtitle file to align with cut video.
        
        Args:
            input_srt: Input SRT file path
            output_srt: Output SRT file path
            removed_segments: List of (start, end) segments removed from video
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(input_srt, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse SRT entries
            entries = self._parse_srt(content)
            
            # Filter profanity from ALL subtitle text (remove profanity words, keep sentences)
            # This removes profanity words but keeps the rest of the sentence
            entries = self._filter_profanity(entries)
            
            # Adjust timestamps to account for removed time
            # This ensures subtitles stay aligned with the cleaned video
            adjusted_entries = self._adjust_timestamps(entries, removed_segments)
            
            # Filter out entries that become completely empty after profanity removal
            # But keep entries that have any remaining text
            final_entries = []
            for entry in adjusted_entries:
                # Keep entry if it has any non-whitespace text
                if entry['text'].strip():
                    final_entries.append(entry)
            
            adjusted_entries = final_entries
            
            # Write output SRT
            self._write_srt(output_srt, adjusted_entries)
            
            return True
            
        except Exception as e:
            print(f"  Error processing subtitles: {e}")
            return False
    
    def _parse_srt(self, content: str) -> List[dict]:
        """Parse SRT content into list of subtitle entries"""
        entries = []
        
        # Split by double newlines (SRT entry separator)
        blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in blocks:
            if not block.strip():
                continue
            
            lines = block.strip().split('\n')
            if len(lines) < 2:
                continue
            
            # First line is index
            try:
                index = int(lines[0])
            except ValueError:
                continue
            
            # Second line is timestamp
            timestamp_line = lines[1]
            time_match = re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})', 
                                 timestamp_line)
            if not time_match:
                continue
            
            # Parse timestamps to seconds
            start_seconds = self._srt_time_to_seconds(time_match.groups()[:4])
            end_seconds = self._srt_time_to_seconds(time_match.groups()[4:])
            
            # Remaining lines are subtitle text
            text = '\n'.join(lines[2:]).strip()
            # Clean VTT timing tags and formatting tags
            text = self._clean_subtitle_text(text)
            
            entries.append({
                'index': index,
                'start': start_seconds,
                'end': end_seconds,
                'text': text
            })
        
        return entries
    
    def _clean_subtitle_text(self, text: str) -> str:
        """Remove VTT timing tags and formatting tags from subtitle text"""
        # Remove VTT timing tags like <00:00:37,260> or <00:00:37.260>
        text = re.sub(r'<00:\d{2}:\d{2}[,.]\d{3}>', '', text)
        # Remove VTT cue tags like <c>...</c>
        text = re.sub(r'<c>', '', text)
        text = re.sub(r'</c>', '', text)
        # Remove any other HTML-like tags
        text = re.sub(r'<[^>]+>', '', text)
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Clean up spaces at start/end of lines
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(line for line in lines if line)
        return text.strip()
    
    def detect_profanity_segments(self, subtitle_path: Path) -> List[Tuple[float, float, str]]:
        """
        Detect profanity in subtitle file and return segments with timestamps.
        
        Args:
            subtitle_path: Path to subtitle file (SRT or VTT)
            
        Returns:
            List of (start_time, end_time, words) tuples for profanity segments
        """
        try:
            with open(subtitle_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse based on file extension
            if subtitle_path.suffix.lower() == '.srt':
                entries = self._parse_srt(content)
            elif subtitle_path.suffix.lower() == '.vtt':
                entries = self._parse_vtt(content)
            else:
                # Try SRT format as default
                entries = self._parse_srt(content)
            
            profanity_segments = []
            
            for entry in entries:
                text = entry['text'].lower()
                # Check if entry contains any profanity
                found_profanity = []
                for word in self.PROFANITY_WORDS:
                    # Use word boundary to match whole words only
                    pattern = r'\b' + re.escape(word) + r'\b'
                    if re.search(pattern, text, re.IGNORECASE):
                        found_profanity.append(word)
                
                if found_profanity:
                    # Add small padding around subtitle segment
                    padding = 0.2
                    profanity_segments.append((
                        max(0, entry['start'] - padding),
                        entry['end'] + padding,
                        ', '.join(sorted(set(found_profanity)))
                    ))
            
            return profanity_segments
            
        except Exception as e:
            print(f"  Error detecting profanity in subtitles: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _filter_profanity(self, entries: List[dict]) -> List[dict]:
        """
        Filter profanity words from subtitle text entries.
        
        Args:
            entries: List of subtitle entry dictionaries
            
        Returns:
            List of entries with profanity filtered
        """
        filtered = []
        profanity_count = 0
        
        for entry in entries:
            original_text = entry['text']
            filtered_text = self._filter_text_profanity(original_text)
            
            if filtered_text != original_text:
                profanity_count += 1
            
            filtered.append({
                'index': entry['index'],
                'start': entry['start'],
                'end': entry['end'],
                'text': filtered_text
            })
        
        if profanity_count > 0:
            print(f"  Filtered profanity from {profanity_count} subtitle entry/entries")
        
        return filtered
    
    def _filter_text_profanity(self, text: str) -> str:
        """
        Filter profanity words from text, removing only the profanity words (not entire sentences).
        
        Args:
            text: Input text to filter
            
        Returns:
            Text with profanity words completely removed, sentences preserved
        """
        if not text:
            return text
        
        # Sort profanity by length (longest first) to match longer words first
        # e.g., "fucking" before "fuck", "motherfucker" before "fuck"
        sorted_profanity = sorted(self.PROFANITY_WORDS, key=len, reverse=True)
        
        # Process each profanity word
        filtered_text = text
        for profanity in sorted_profanity:
            # Create regex pattern that matches the profanity word as a whole word
            # \b ensures word boundaries, so "class" won't match "ass"
            # Match word with optional punctuation after it
            # Use word boundary to ensure we only match complete words
            pattern = r'\b' + re.escape(profanity) + r'\b'
            
            # Remove only the profanity word itself (case-insensitive)
            # This preserves the sentence structure
            filtered_text = re.sub(pattern, '', filtered_text, flags=re.IGNORECASE)
        
        # Clean up extra spaces that might result from word removal
        # Replace multiple spaces with single space
        filtered_text = re.sub(r' +', ' ', filtered_text)
        # Remove space before punctuation
        filtered_text = re.sub(r'\s+([.,!?;:])', r'\1', filtered_text)
        # Remove space after punctuation if followed by space
        filtered_text = re.sub(r'([.,!?;:])\s+', r'\1 ', filtered_text)
        # Clean up any double spaces that might remain
        filtered_text = re.sub(r'  +', ' ', filtered_text)
        # Remove leading/trailing spaces
        filtered_text = filtered_text.strip()
        
        return filtered_text
    
    def _srt_time_to_seconds(self, time_parts: Tuple[str, str, str, str]) -> float:
        """Convert SRT time format (HH:MM:SS,mmm) to seconds"""
        hours, minutes, seconds, milliseconds = map(int, time_parts)
        return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _filter_entries(self, entries: List[dict], 
                       removed_segments: List[Tuple[float, float]]) -> List[dict]:
        """Remove subtitle entries that overlap with removed segments"""
        filtered = []
        
        # Sort removed segments for efficient checking
        sorted_removed = sorted(removed_segments, key=lambda x: x[0])
        
        for entry in entries:
            entry_start = entry['start']
            entry_end = entry['end']
            
            # Check if entry overlaps with any removed segment
            should_remove = False
            for remove_start, remove_end in sorted_removed:
                # Remove if entry overlaps with removed segment
                # Overlap condition: entry starts before remove ends AND entry ends after remove starts
                # Also remove if entry is completely within removed segment
                # Also remove if entry starts within removed segment (even if it extends beyond)
                if (entry_start < remove_end and entry_end > remove_start):
                    should_remove = True
                    break
                # Also check: if entry starts very close after removed segment, it might be affected
                # But we'll handle this in adjustment - if adjusted time falls in removed segment, skip it
            
            if not should_remove:
                filtered.append(entry)
        
        return filtered
    
    def _adjust_timestamps(self, entries: List[dict], 
                          removed_segments: List[Tuple[float, float]]) -> List[dict]:
        """
        Adjust subtitle timestamps to account for removed time.
        
        For each subtitle, subtract the cumulative duration of all removed segments
        that occurred completely before this subtitle's start time.
        Keeps all entries - profanity words have already been removed from text.
        """
        if not removed_segments:
            return entries
        
        # Sort removed segments by start time
        sorted_removed = sorted(removed_segments, key=lambda x: x[0])
        
        adjusted = []
        for entry in entries:
            entry_start = entry['start']
            entry_end = entry['end']
            
            # Calculate total time removed before this entry
            # Count ALL segments that end before entry_start
            time_removed_before = 0.0
            for remove_start, remove_end in sorted_removed:
                if remove_end <= entry_start:
                    # Entire removal happened before this entry
                    time_removed_before += (remove_end - remove_start)
                # Don't break - need to check all segments that end before entry_start
            
            # Adjust timestamps by subtracting cumulative removed time
            new_start = max(0.0, entry_start - time_removed_before)
            new_end = max(0.0, entry_end - time_removed_before)
            
            # Ensure end is after start
            if new_end <= new_start:
                new_end = new_start + 0.1
            
            # Keep all entries (don't filter out overlapping ones)
            # Profanity words have already been removed from the text
            adjusted.append({
                'index': entry['index'],
                'start': new_start,
                'end': new_end,
                'text': entry['text']
            })
        
        return adjusted
    
    def _write_srt(self, output_path: Path, entries: List[dict]):
        """Write subtitle entries to SRT file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, entry in enumerate(entries, 1):
                f.write(f"{i}\n")
                f.write(f"{self._seconds_to_srt_time(entry['start'])} --> {self._seconds_to_srt_time(entry['end'])}\n")
                f.write(f"{entry['text']}\n")
                f.write("\n")
    
    def process_vtt(self, input_vtt: Path, output_vtt: Path,
                    removed_segments: List[Tuple[float, float]]) -> bool:
        """
        Process VTT subtitle file to align with cut video.
        
        Args:
            input_vtt: Input VTT file path
            output_vtt: Output VTT file path
            removed_segments: List of (start, end) segments removed from video
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(input_vtt, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse VTT entries
            entries = self._parse_vtt(content)
            
            # Filter out entries that fall within removed segments
            filtered_entries = self._filter_entries(entries, removed_segments)
            
            # Adjust timestamps to account for removed time
            adjusted_entries = self._adjust_timestamps(filtered_entries, removed_segments)
            
            # Filter profanity from remaining subtitle text
            filtered_entries = self._filter_profanity(adjusted_entries)
            
            # Write output VTT
            self._write_vtt(output_vtt, filtered_entries)
            
            return True
            
        except Exception as e:
            print(f"  Error processing VTT subtitles: {e}")
            return False
    
    def _parse_vtt(self, content: str) -> List[dict]:
        """Parse VTT content into list of subtitle entries"""
        entries = []
        
        # Remove WEBVTT header and metadata
        lines = content.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('WEBVTT'):
                start_idx = i + 1
                break
        
        # Find cue blocks
        current_cue = None
        for line in lines[start_idx:]:
            line = line.strip()
            if not line:
                if current_cue:
                    entries.append(current_cue)
                    current_cue = None
                continue
            
            # Check if line is a timestamp
            time_match = re.match(r'(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})\.(\d{3})', 
                                 line)
            if time_match:
                if current_cue:
                    entries.append(current_cue)
                
                start_seconds = self._vtt_time_to_seconds(time_match.groups()[:4])
                end_seconds = self._vtt_time_to_seconds(time_match.groups()[4:])
                
                current_cue = {
                    'index': len(entries) + 1,
                    'start': start_seconds,
                    'end': end_seconds,
                    'text': ''
                }
            elif current_cue:
                # Add text to current cue
                if current_cue['text']:
                    current_cue['text'] += '\n' + line
                else:
                    current_cue['text'] = line
        
        if current_cue:
            entries.append(current_cue)
        
        # Clean all entries
        for entry in entries:
            entry['text'] = self._clean_subtitle_text(entry['text'])
        
        return entries
    
    def _vtt_time_to_seconds(self, time_parts: Tuple[str, str, str, str]) -> float:
        """Convert VTT time format (HH:MM:SS.mmm) to seconds"""
        hours, minutes, seconds, milliseconds = map(int, time_parts)
        return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
    
    def _seconds_to_vtt_time(self, seconds: float) -> str:
        """Convert seconds to VTT time format (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    
    def _write_vtt(self, output_path: Path, entries: List[dict]):
        """Write subtitle entries to VTT file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for entry in entries:
                f.write(f"{self._seconds_to_vtt_time(entry['start'])} --> {self._seconds_to_vtt_time(entry['end'])}\n")
                f.write(f"{entry['text']}\n\n")

