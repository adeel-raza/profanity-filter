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
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
# Removed multiprocessing - using sequential extraction with optimized CRF values
import os


# Removed _extract_single_segment_worker - using sequential extraction instead

class VideoCutter:
    """Cuts out segments from video using FFmpeg with optimized CPU encoding"""

    def __init__(self):
        pass
    
    def cut_segments(self, input_path: Path, output_path: Path,
                     segments_to_remove: List[Tuple[float, float]],
                     mute_only: bool = False) -> bool:
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

        if mute_only:
            print("  Mute-only mode enabled: preserving timeline and muting audio in detected intervals")
            return self._mute_segments(input_path, output_path, final_segments)
        
        # Calculate segments to KEEP (inverse of segments to remove)
        keep_segments = self._calculate_keep_segments(final_segments, duration)
        
        if not keep_segments:
            print("  Warning: All video would be removed. Creating empty video.")
            return False
        
        # Build FFmpeg filter to keep only specified segments
        # Get original video bitrate to match quality
        original_bitrate = self._get_video_bitrate(input_path)
        return self._apply_cuts(input_path, output_path, keep_segments, original_bitrate)

    def _mute_segments(self, input_path: Path, output_path: Path,
                       segments_to_mute: List[Tuple[float, float]]) -> bool:
        """Mute audio only in the provided time intervals while preserving video duration."""
        if not segments_to_mute:
            print("  No segments to mute - copying video as-is")
            import shutil
            shutil.copy2(input_path, output_path)
            return True

        audio_info = self._get_audio_stream_info(input_path)
        enable_expr = self._build_mute_enable_expr(segments_to_mute)
        if not enable_expr:
            print("  No valid mute intervals - copying video as-is")
            import shutil
            shutil.copy2(input_path, output_path)
            return True

        # Portable across modern FFmpeg: avoid non-portable -filter_script:a.
        audio_filter = f"volume=0:enable='{enable_expr}'"
        audio_encode_args = self._build_audio_encode_args(audio_info)

        channels = audio_info.get('channels')
        layout = audio_info.get('channel_layout') or 'unknown'
        bitrate = audio_info.get('bit_rate')
        print(
            "  Audio profile: "
            f"channels={channels if channels else 'unknown'}, "
            f"layout={layout}, "
            f"bitrate={bitrate // 1000 if isinstance(bitrate, int) else 'unknown'}k"
        )

        try:
            if len(audio_filter) <= 6000:
                cmd = [
                    'ffmpeg', '-i', str(input_path),
                    '-map', '0:v:0?',
                    '-map', '0:a:0?',
                    '-c:v', 'copy',
                    '-af', audio_filter,
                    *audio_encode_args,
                    '-loglevel', 'error',
                    '-y', str(output_path)
                ]
                if output_path.suffix.lower() == '.mp4':
                    # Insert before loglevel for MP4 streaming-friendly output.
                    cmd[cmd.index('-loglevel'):cmd.index('-loglevel')] = ['-movflags', '+faststart']
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print("  ✓ Audio muting complete")
                    return True
                print("  ✗ FFmpeg mute command failed. Return code:", result.returncode)
                if result.stderr:
                    err_lines = [l for l in result.stderr.splitlines() if l.strip()]
                    print("    " + '\n    '.join(err_lines[:12]))
                return False

            return self._mute_segments_via_filter_script(
                input_path=input_path,
                output_path=output_path,
                audio_filter=audio_filter,
                audio_encode_args=audio_encode_args,
            )
        except Exception as e:
            print(f"  Error during mute-only processing: {e}")
            return False

    def _mute_segments_via_filter_script(
        self,
        input_path: Path,
        output_path: Path,
        audio_filter: str,
        audio_encode_args: List[str],
    ) -> bool:
        """Mute using filter_complex_script for very long mute expressions."""
        filter_script_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.fffilter', delete=False) as script_file:
                script_file.write(f"[0:a:0]{audio_filter}[aout]\n")
                filter_script_path = script_file.name

            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-filter_complex_script', filter_script_path,
                '-map', '0:v:0?',
                '-map', '[aout]',
                '-c:v', 'copy',
                *audio_encode_args,
                '-loglevel', 'error',
                '-y', str(output_path)
            ]
            if output_path.suffix.lower() == '.mp4':
                cmd[cmd.index('-loglevel'):cmd.index('-loglevel')] = ['-movflags', '+faststart']
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("  ✓ Audio muting complete")
                return True

            print("  ✗ FFmpeg mute command failed. Return code:", result.returncode)
            if result.stderr:
                err_lines = [l for l in result.stderr.splitlines() if l.strip()]
                print("    " + '\n    '.join(err_lines[:12]))
            return False
        finally:
            if filter_script_path and os.path.exists(filter_script_path):
                try:
                    os.remove(filter_script_path)
                except OSError:
                    pass

    def _build_mute_enable_expr(self, segments: List[Tuple[float, float]]) -> str:
        """Build a compact enable expression for volume mute intervals."""
        parts = []
        for start, end in segments:
            if end <= start:
                continue
            parts.append(f"between(t,{start:.3f},{end:.3f})")
        return "+".join(parts)

    def _get_audio_stream_info(self, video_path: Path) -> Dict[str, Optional[object]]:
        """Inspect primary audio stream so mute re-encode preserves quality."""
        info: Dict[str, Optional[object]] = {
            'channels': None,
            'channel_layout': None,
            'bit_rate': None,
            'sample_rate': None,
            'codec_name': None,
        }
        try:
            cmd = [
                'ffprobe', '-v', 'error',
                '-select_streams', 'a:0',
                '-show_entries', 'stream=channels,channel_layout,bit_rate,sample_rate,codec_name',
                '-of', 'default=noprint_wrappers=1',
                str(video_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines():
                if '=' not in line:
                    continue
                key, value = line.split('=', 1)
                value = value.strip()
                if not value or value == 'N/A':
                    continue
                if key == 'channels':
                    info['channels'] = int(float(value))
                elif key == 'channel_layout':
                    info['channel_layout'] = value
                elif key == 'bit_rate':
                    info['bit_rate'] = int(float(value))
                elif key == 'sample_rate':
                    info['sample_rate'] = int(float(value))
                elif key == 'codec_name':
                    info['codec_name'] = value
        except Exception:
            pass
        return info

    def _build_audio_encode_args(self, audio_info: Dict[str, Optional[object]]) -> List[str]:
        """Choose AAC encode settings that preserve channel count and quality."""
        args = ['-c:a', 'aac']

        channels = audio_info.get('channels')
        if isinstance(channels, int) and channels > 0:
            # Preserve surround/stereo instead of silently downmixing to mono/default.
            args.extend(['-ac', str(channels)])

        sample_rate = audio_info.get('sample_rate')
        if isinstance(sample_rate, int) and sample_rate > 0:
            args.extend(['-ar', str(sample_rate)])

        bit_rate = audio_info.get('bit_rate')
        if isinstance(bit_rate, int) and bit_rate > 0:
            target = max(160000, min(bit_rate, 640000))
        else:
            ch = channels if isinstance(channels, int) and channels > 0 else 2
            target = max(160000, min(96000 * ch, 640000))
        args.extend(['-b:a', str(target)])
        return args

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
    
    
