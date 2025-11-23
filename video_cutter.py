"""
Video Cutter - Cuts out segments from video using FFmpeg
"""

import subprocess
from pathlib import Path
from typing import List, Tuple


class VideoCutter:
    """Cuts out segments from video using FFmpeg"""
    
    def cut_segments(self, input_path: Path, output_path: Path, 
                     segments_to_remove: List[Tuple[float, float]]) -> bool:
        """
        Cut out specified segments from video.
        
        Args:
            input_path: Input video file
            output_path: Output video file
            segments_to_remove: List of (start, end) tuples to remove
            
        Returns:
            True if successful, False otherwise
        """
        if not segments_to_remove:
            # No segments to remove, just copy
            print("  No segments to remove - copying video as-is")
            import shutil
            shutil.copy2(input_path, output_path)
            return True
        
        print(f"  Processing {len(segments_to_remove)} segment(s) to remove...")
        
        # Validate segments
        valid_segments = []
        for i, (start, end) in enumerate(segments_to_remove, 1):
            if start < 0 or end < 0:
                print(f"  Warning: Segment {i} has negative time ({start}, {end}) - skipping")
                continue
            if start >= end:
                print(f"  Warning: Segment {i} invalid (start >= end): ({start}, {end}) - skipping")
                continue
            valid_segments.append((start, end))
        
        if not valid_segments:
            print("  Error: No valid segments to remove after validation")
            return False
        
        if len(valid_segments) != len(segments_to_remove):
            print(f"  Warning: {len(segments_to_remove) - len(valid_segments)} invalid segment(s) were skipped")
        
        total_removed = sum(end - start for start, end in valid_segments)
        print(f"  Total time to remove: {total_removed:.2f} seconds ({total_removed/60:.2f} minutes)")
        
        # Get video duration
        duration = self._get_duration(input_path)
        if duration is None:
            print("  Error: Could not get video duration")
            return False
        
        # Validate segments don't exceed video duration
        final_segments = []
        for start, end in valid_segments:
            if start > duration:
                print(f"  Warning: Segment starts after video end ({start:.2f}s > {duration:.2f}s) - skipping")
                continue
            if end > duration:
                print(f"  Warning: Segment extends beyond video end, truncating to {duration:.2f}s")
                end = duration
            final_segments.append((start, end))
        
        if not final_segments:
            print("  Warning: No valid segments after duration validation - copying video as-is")
            import shutil
            shutil.copy2(input_path, output_path)
            return True
        
        # Calculate segments to KEEP (inverse of segments to remove)
        keep_segments = self._calculate_keep_segments(final_segments, duration)
        
        if not keep_segments:
            print("  Warning: All video would be removed. Creating empty video.")
            return False
        
        # Build FFmpeg filter to keep only specified segments
        return self._apply_cuts(input_path, output_path, keep_segments)
    
    def _get_duration(self, video_path: Path) -> float:
        """Get video duration in seconds"""
        try:
            cmd = [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(video_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except Exception:
            return None
    
    def _calculate_keep_segments(self, remove_segments: List[Tuple[float, float]], 
                                 duration: float) -> List[Tuple[float, float]]:
        """Calculate segments to keep (inverse of segments to remove)"""
        if not remove_segments:
            return [(0.0, duration)]
        
        # Sort remove segments
        remove_segments = sorted(remove_segments, key=lambda x: x[0])
        
        keep_segments = []
        current_time = 0.0
        
        for remove_start, remove_end in remove_segments:
            # If there's a gap before this removal, keep it
            if current_time < remove_start:
                keep_segments.append((current_time, remove_start))
            current_time = max(current_time, remove_end)
        
        # Keep everything after last removal
        if current_time < duration:
            keep_segments.append((current_time, duration))
        
        return keep_segments
    
    def _apply_cuts(self, input_path: Path, output_path: Path, 
                    keep_segments: List[Tuple[float, float]], use_qsv_override: bool = None) -> bool:
        """Apply cuts using FFmpeg"""
        
        # Check for Intel QSV support (only if not explicitly overridden)
        if use_qsv_override is not None:
            use_qsv = use_qsv_override
        else:
            # Properly check for QSV encoder support
            try:
                result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], 
                                      capture_output=True, text=True, check=True)
                use_qsv = 'h264_qsv' in result.stdout
                if use_qsv:
                    print("  ✓ Intel Quick Sync Video (QSV) detected - attempting hardware acceleration")
                else:
                    print("  Intel QSV not detected - using CPU encoding")
            except:
                use_qsv = False
                print("  Intel QSV not detected - using CPU encoding")

        try:
            # Use filter_complex with concat for more reliable segment cutting
            if len(keep_segments) == 1:
                # Single segment - use re-encoding for accuracy
                start, end = keep_segments[0]
                duration = end - start
                # Use -ss after -i for accurate timing
                cmd = [
                    'ffmpeg', '-i', str(input_path),
                    '-ss', str(start),
                    '-t', str(duration),
                    '-c:v', 'libx264',  # Re-encode video for accuracy
                    '-c:a', 'aac',  # Re-encode audio for accuracy
                    '-preset', 'fast',  # Balance speed and quality
                    '-crf', '23',  # Good quality
                    '-avoid_negative_ts', 'make_zero',
                    '-y', str(output_path)
                ]

            else:
                # Multiple segments - use stream copy for speed (no re-encoding)
                import tempfile
                temp_dir = Path(tempfile.mkdtemp())
                segment_files = []
                total_segments = len(keep_segments)
                
                print(f"  Extracting {total_segments} segments (re-encoding for accuracy - slower but precise)...")
                for i, (start, end) in enumerate(keep_segments, 1):
                    duration = end - start
                    segment_file = temp_dir / f'segment_{i:04d}.mp4'
                    segment_files.append(segment_file)
                    
                    print(f"    Extracting segment {i}/{total_segments}: {start:.1f}s - {end:.1f}s ({duration:.1f}s)...", end='\r')
                    
                    # Extract segment using re-encoding (SLOWER but more accurate timing)
                    # Re-encoding ensures precise frame boundaries and accurate timing
                    extract_cmd = [
                        'ffmpeg', '-i', str(input_path),
                        '-ss', str(start),
                        '-t', str(duration),
                        '-c:v', 'libx264',  # Re-encode video for accuracy
                        '-c:a', 'aac',  # Re-encode audio for accuracy
                        '-preset', 'fast',  # Balance speed and quality
                        '-crf', '23',  # Good quality
                        '-avoid_negative_ts', 'make_zero',
                        '-loglevel', 'error',
                        '-y', str(segment_file)
                    ]

                    subprocess.run(extract_cmd, capture_output=True, check=True)
                
                print()  # New line after progress
                print(f"  ✓ All segments extracted (re-encoded for accuracy)")
                
                # Create concat file
                concat_file = temp_dir / 'concat.txt'
                with open(concat_file, 'w') as f:
                    for seg_file in segment_files:
                        f.write(f"file '{seg_file.absolute()}'\n")
                
                # Concatenate segments
                print(f"  Concatenating {total_segments} segments into final video...")
                cmd = [
                    'ffmpeg', '-f', 'concat',
                    '-safe', '0',
                    '-i', str(concat_file),
                    '-c', 'copy',  # Copy streams for speed
                    '-fflags', '+genpts',  # Generate presentation timestamps for accurate duration
                    '-loglevel', 'error',
                    '-y', str(output_path)
                ]
            
            if len(keep_segments) == 1:
                print(f"  Processing single segment with FFmpeg...")
            else:
                print(f"  Final concatenation (this may take a few minutes)...")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"  ✓ Video cutting complete")
            return True
        
        except subprocess.CalledProcessError as e:
            if use_qsv:
                print(f"  Warning: QSV hardware encoding failed. Retrying with CPU encoding...")
                # Retry with QSV forced off
                return self._apply_cuts(input_path, output_path, keep_segments, use_qsv_override=False)
            
            print(f"  Error: FFmpeg failed")
            if e.stderr:
                error_msg = e.stderr if isinstance(e.stderr, str) else e.stderr.decode('utf-8', errors='ignore')
                print(f"  {error_msg[:1000]}")
            return False
        except Exception as e:
            if use_qsv:
                 print(f"  Warning: Error during QSV encoding ({e}). Retrying with CPU encoding...")
                 return self._apply_cuts(input_path, output_path, keep_segments, use_qsv_override=False)

            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            return False

