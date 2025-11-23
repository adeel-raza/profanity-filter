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
            
            # First, identify entries that should be removed or clipped
            # Use ORIGINAL timestamps for this check (before adjustment)
            entries_to_process = []
            for entry in entries:
                entry_start = entry['start']  # Original timestamp
                entry_end = entry['end']      # Original timestamp
                
                # Check if entry is completely within a removed segment
                completely_removed = False
                for remove_start, remove_end in removed_segments:
                    if entry_start >= remove_start and entry_end <= remove_end:
                        completely_removed = True
                        break
                
                # Skip entries completely within removed segments
                if completely_removed:
                    continue
                
                # Check if entry starts inside a removal (should only keep part after removal)
                starts_in_removal = False
                for remove_start, remove_end in removed_segments:
                    if remove_start <= entry_start < remove_end:
                        starts_in_removal = True
                        # If entry starts in removal, only keep part after removal
                        if entry_end > remove_end:
                            entries_to_process.append({
                                'index': entry['index'],
                                'start': remove_end,
                                'end': entry_end,
                                'text': entry['text']
                            })
                        # If entry ends within removal, it's completely removed
                        break
                
                if starts_in_removal:
                    continue
                
                # For entries that overlap with removed segments, clip them
                # Keep only the parts that are NOT in removed segments
                clipped_entries = self._clip_entry_to_keep_segments(
                    entry, removed_segments
                )
                entries_to_process.extend(clipped_entries)
            
            # Now adjust timestamps for entries we're keeping
            # This ensures subtitles stay aligned with the cleaned video
            adjusted_entries = self._adjust_timestamps(entries_to_process, removed_segments)
            
            # Filter out entries that have no text after profanity removal
            final_entries = []
            for entry in adjusted_entries:
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
                
                # First check for multi-word phrases (e.g., "fuck you", "ass hole")
                multi_word_phrases = [
                    ('fuck you', 'fuckyou'),
                    ('fuck off', 'fuckoff'),
                    ('ass hole', 'asshole'),
                    ('mother fucker', 'motherfucker'),
                    ('mother fuck', 'motherfuck'),
                ]
                
                for phrase, word_key in multi_word_phrases:
                    if word_key in self.PROFANITY_WORDS:
                        pattern = r'\b' + re.escape(phrase) + r'\b'
                        if re.search(pattern, text, re.IGNORECASE):
                            found_profanity.append(word_key)
                
                # Then check individual words
                for word in self.PROFANITY_WORDS:
                    # Use word boundary to match whole words only
                    pattern = r'\b' + re.escape(word) + r'\b'
                    if re.search(pattern, text, re.IGNORECASE):
                        if word not in found_profanity:  # Avoid duplicates
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
        
        # First handle multi-word phrases (e.g., "fuck you", "ass hole")
        multi_word_phrases = [
            ('fuck you', 'fuckyou'),
            ('fuck off', 'fuckoff'),
            ('ass hole', 'asshole'),
            ('mother fucker', 'motherfucker'),
            ('mother fuck', 'motherfuck'),
        ]
        
        filtered_text = text
        for phrase, word_key in multi_word_phrases:
            if word_key in self.PROFANITY_WORDS:
                # Match phrase with word boundaries, case-insensitive
                pattern = r'\b' + re.escape(phrase) + r'\b'
                filtered_text = re.sub(pattern, '', filtered_text, flags=re.IGNORECASE)
        
        # Sort profanity by length (longest first) to match longer words first
        # e.g., "fucking" before "fuck", "motherfucker" before "fuck"
        sorted_profanity = sorted(self.PROFANITY_WORDS, key=len, reverse=True)
        
        # Process each profanity word
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
    
    def _clip_entry_to_keep_segments(self, entry: dict, 
                                     removed_segments: List[Tuple[float, float]]) -> List[dict]:
        """
        Clip an entry to only keep parts that are NOT in removed segments.
        Returns a list of entry dicts (may be empty, or 1-2 entries if split).
        
        Example: Entry 12-18 with removal 10-15:
        - Part 12-15 is removed (overlaps removal)
        - Part 15-18 is kept (after removal)
        - Returns entry for 15-18 only
        """
        entry_start = entry['start']
        entry_end = entry['end']
        entry_text = entry['text']
        entry_index = entry['index']
        
        # Sort removed segments
        sorted_removed = sorted(removed_segments, key=lambda x: x[0])
        
        # Find all keep segments (parts of entry that don't overlap removals)
        keep_segments = []
        current_time = entry_start
        
        for remove_start, remove_end in sorted_removed:
            # Check if this removal overlaps with the entry
            if entry_start < remove_end and entry_end > remove_start:
                # Keep part before removal (if any)
                if current_time < remove_start:
                    keep_segments.append((current_time, remove_start))
                # Move current_time past the removal
                current_time = max(current_time, remove_end)
        
        # Keep part after last removal (if any)
        if current_time < entry_end:
            keep_segments.append((current_time, entry_end))
        
        # If no keep segments, entry is completely removed
        if not keep_segments:
            return []
        
        # Create entry dicts for each keep segment
        result = []
        for keep_start, keep_end in keep_segments:
            if keep_end > keep_start:  # Valid segment
                result.append({
                    'index': entry_index,
                    'start': keep_start,
                    'end': keep_end,
                    'text': entry_text
                })
        
        return result
    
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
        Adjust subtitle timestamps to match the cleaned video.
        
        This matches the video cutter's exact logic:
        1. Video cutter keeps segments: (0, r1_start), (r1_end, r2_start), ..., (rN_end, video_end)
        2. For each subtitle, find which keep segment it's in
        3. Map to the corresponding position in the cleaned video
        """
        if not removed_segments:
            return entries
        
        # Calculate keep segments (same as video cutter)
        sorted_removed = sorted(removed_segments, key=lambda x: x[0])
        keep_segments_original = []
        current_time = 0.0
        
        for remove_start, remove_end in sorted_removed:
            if current_time < remove_start:
                keep_segments_original.append((current_time, remove_start))
            current_time = max(current_time, remove_end)
        # Add final segment (we use a large number, actual duration doesn't matter for mapping)
        keep_segments_original.append((current_time, float('inf')))
        
        def map_timestamp(original_time: float) -> float:
            """Map original timestamp to cleaned video timestamp"""
            # Find which keep segment this timestamp is in
            for keep_start, keep_end in keep_segments_original:
                if keep_start <= original_time < keep_end:
                    # Calculate position within this keep segment
                    position_in_segment = original_time - keep_start
                    
                    # Calculate where this keep segment starts in cleaned video
                    # Sum all removals that happened before this keep segment
                    time_removed_before = 0.0
                    for remove_start, remove_end in sorted_removed:
                        if remove_end <= keep_start:
                            time_removed_before += (remove_end - remove_start)
                    
                    # In cleaned video, this keep segment starts at (keep_start - time_removed_before)
                    cleaned_start = keep_start - time_removed_before
                    
                    # Map the timestamp
                    mapped_time = cleaned_start + position_in_segment
                    
                    # Return mapped time without delay first
                    # Delay will be added only if needed based on testing
                    return mapped_time
            
            # If timestamp is at or after last keep segment, calculate total removed
            total_removed = sum(end - start for start, end in sorted_removed)
            return original_time - total_removed + 0.3  # Add delay
        
        adjusted = []
        for entry in entries:
            orig_start = entry['start']
            orig_end = entry['end']
            
            # Map both start and end timestamps
            new_start = map_timestamp(orig_start)
            new_end = map_timestamp(orig_end)
            
            # Ensure end is after start
            if new_end <= new_start:
                new_end = new_start + 0.1
            
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

