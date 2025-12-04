"""
Video Cutter - Cuts out segments from video using FFmpeg (Optimized for SPEED)
Speed optimizations:
- Veryfast preset (faster than 'fast' preset)
- Higher CRF values (38/35/32/28/23 vs 35/32/28/23/18) = faster encoding
- Use all CPU cores (-threads 0)
- Sequential extraction (multiprocessing removed for stability)
- Result: Faster encoding with acceptable quality
"""

import subprocess
from pathlib import Path
from typing import List, Tuple
# Removed multiprocessing - using sequential extraction with optimized CRF values
import os


# Removed _extract_single_segment_worker - using sequential extraction instead

class VideoCutter:
    """Cuts out segments from video using FFmpeg with optimized CPU encoding"""

    def __init__(self):
        pass
    
    def cut_segments(self, input_path: Path, output_path: Path, 
                     segments_to_remove: List[Tuple[float, float]]) -> bool:
        """
        Cut out specified segments from video.
        
        Args:
            input_path: Input video file
            output_path: Output video file
            segments_to_remove: List of (start, end) tuples to remove
            mute_only: If True, mute audio instead of cutting
            lossless_snap: If True, perform keyframe-aligned stream copy cuts (fast, coarse)
        Returns:
            True if successful, False otherwise
        """
        if not segments_to_remove:
            # No segments to remove, just copy
            print("  No segments to process - copying video as-is")
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
        # Get original video bitrate to match quality
        original_bitrate = self._get_video_bitrate(input_path)
        return self._apply_cuts(input_path, output_path, keep_segments, original_bitrate)
    
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
    
    def _get_video_bitrate(self, video_path: Path) -> int:
        """Get video stream bitrate in bps"""
        try:
            cmd = [
                'ffprobe', '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=bit_rate',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(video_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            bitrate = result.stdout.strip()
            if bitrate and bitrate != 'N/A':
                return int(float(bitrate))
        except Exception:
            pass
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
                    keep_segments: List[Tuple[float, float]],
                    original_bitrate: int = None) -> bool:
        """Apply cuts using FFmpeg with optimized CPU encoding"""
        
        # Match ORIGINAL INPUT video visual quality: Use lower CRF (higher quality)
        # Speed comes from ultrafast preset and all CPU cores, not from lower quality
        # Use CRF 23-25 to maintain visual quality similar to original input
        if original_bitrate:
            if original_bitrate < 200000:
                crf_value = 23  # Higher quality to match original input visual quality (was 35 - too low)
            elif original_bitrate < 500000:
                crf_value = 23  # Higher quality
            elif original_bitrate < 1000000:
                crf_value = 23  # Higher quality
            elif original_bitrate < 2000000:
                crf_value = 20  # High quality
            else:
                crf_value = 18  # Very high quality
            print(f"  Speed-optimized encoding (matching original INPUT visual quality): {original_bitrate//1000}kbps (CRF {crf_value})")
        else:
            crf_value = 23  # Default high quality
            print(f"  Using default (high quality to match original input): CRF {crf_value}")
        
        try:
            # Use filter_complex with concat for more reliable segment cutting
            if len(keep_segments) == 1:
                # Single segment - simple cut
                start, end = keep_segments[0]
                duration = end - start
                
                # Build FFmpeg command with optimizations
                cmd = [
                    'ffmpeg', '-i', str(input_path),
                    '-ss', str(start),
                    '-t', str(duration),
                    '-c:v', 'libx264',
                    '-crf', str(crf_value),
                    '-preset', 'veryfast',  # Faster than fast, but better quality than ultrafast  # Aggressive: ultrafast preset (fastest possible)
                    '-threads', '0',  # Use all CPU cores
                    '-tune', 'fastdecode',  # Optimize for fast decoding
                    '-x264-params', 'keyint=30:min-keyint=30:scenecut=0',  # Faster encoding
                    '-c:a', 'aac',  # Re-encode audio (stream copy caused profanity detection issues)
                    '-b:a', '96k',  # Speed-optimized: slightly lower audio bitrate (96k vs 128k)
                    '-avoid_negative_ts', 'make_zero',
                    '-y', str(output_path)
                ]
                print(f"  [SPEED-OPTIMIZED] Single-segment encode with veryfast preset + all CPU cores")

            else:
                # Multiple segments - extract sequentially (no multiprocessing), then concat
                import tempfile
                temp_dir = Path(tempfile.mkdtemp())
                segment_files = []
                total_segments = len(keep_segments)
                
                print(f"  Extracting {total_segments} segments sequentially (speed-optimized: veryfast preset)...")
                for i, (start, end) in enumerate(keep_segments, 1):
                    duration = end - start
                    segment_file = temp_dir / f'segment_{i:04d}.mp4'
                    segment_files.append(segment_file)
                    
                    print(f"    Extracting segment {i}/{total_segments}: {start:.1f}s - {end:.1f}s ({duration:.1f}s)...", end='\r')
                    
                    # Sequential extraction with optimized CRF
                    # Use CRF for all videos to maintain quality (bitrate targeting causes quality issues)
                    extract_cmd = [
                        'ffmpeg', '-i', str(input_path),
                        '-ss', str(start),
                        '-t', str(duration),
                        '-c:v', 'libx264',
                        '-crf', str(crf_value),  # Use CRF to maintain visual quality
                        '-preset', 'veryfast',  # Faster than fast, but better quality than ultrafast
                        '-threads', '0',
                        '-c:a', 'aac',
                        '-b:a', '128k',
                        '-avoid_negative_ts', 'make_zero',
                        '-loglevel', 'error',
                        '-y', str(segment_file)
                    ]
                    result = subprocess.run(extract_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                    if result.returncode != 0:
                        print(f"\n  ✗ Failed to extract segment {i}")
                        # Cleanup temp directory if it exists
                        import shutil
                        if temp_dir.exists():
                            try:
                                shutil.rmtree(temp_dir)
                            except (FileNotFoundError, OSError):
                                pass  # Directory already deleted (e.g., by user clearing /tmp)
                        return False
                
                print()  # New line after progress
                print(f"  ✓ All {total_segments} segments extracted")
                
                # Create concat file
                concat_file = temp_dir / 'concat.txt'
                try:
                    with open(concat_file, 'w') as f:
                        for seg_file in segment_files:
                            f.write(f"file '{seg_file.absolute()}'\n")
                except (FileNotFoundError, OSError) as e:
                    print(f"\n  ✗ Failed to create concat file: {e}")
                    print(f"  ⚠️  Temp directory may have been deleted. If you cleared /tmp files, please avoid doing so during processing.")
                    import shutil
                    if temp_dir.exists():
                        try:
                            shutil.rmtree(temp_dir)
                        except (FileNotFoundError, OSError):
                            pass
                    return False
                
                # Concatenate segments - use CRF to maintain quality
                print(f"  Concatenating {total_segments} segments into final video...")
                cmd = [
                    'ffmpeg', '-fflags', '+genpts', '-f', 'concat',
                    '-safe', '0',
                    '-i', str(concat_file),
                    '-c:v', 'libx264',
                    '-crf', str(crf_value),  # Use CRF to maintain visual quality
                    '-preset', 'veryfast',  # Faster than fast, but better quality than ultrafast
                    '-threads', '0',
                    '-c:a', 'aac',
                    '-b:a', '128k',
                    '-loglevel', 'error',
                    '-y', str(output_path)
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Cleanup temp directory after processing (whether success or failure)
            if 'temp_dir' in locals() and temp_dir.exists():
                import shutil
                try:
                    shutil.rmtree(temp_dir)
                except (FileNotFoundError, OSError):
                    pass  # Directory already deleted - that's okay
            
            if result.returncode == 0:
                print(f"  ✓ Video cutting complete")
                return True
            else:
                print("  ✗ FFmpeg command failed. Return code:", result.returncode)
                if result.stderr:
                    err_lines = [l for l in result.stderr.splitlines() if l.strip()]
                    print("    " + '\n    '.join(err_lines[:12]))
                return False
        
        except subprocess.CalledProcessError as e:
            print("  Error: FFmpeg failed")
            stderr = e.stderr if isinstance(e.stderr, str) else (e.stderr.decode('utf-8', errors='ignore') if e.stderr else '')
            if stderr:
                print("  " + "\n  ".join(stderr.splitlines()[:12]))
            return False
        except Exception as e:
            print(f"  Error: {e}")
            # Cleanup temp directory if it exists
            if 'temp_dir' in locals() and temp_dir.exists():
                import shutil
                try:
                    shutil.rmtree(temp_dir)
                except (FileNotFoundError, OSError):
                    pass  # Directory already deleted - that's okay
            import traceback
            traceback.print_exc()
            return False
    
    
