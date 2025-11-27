"""
Video Cutter - Cuts out segments from video using FFmpeg
"""

import subprocess
from pathlib import Path
from typing import List, Tuple


class VideoCutter:
    """Cuts out segments from video using FFmpeg or mutes audio in segments"""
    
    def cut_segments(self, input_path: Path, output_path: Path, 
                     segments_to_remove: List[Tuple[float, float]], mute_only: bool = False) -> bool:
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
            print("  No segments to process - copying video as-is")
            import shutil
            shutil.copy2(input_path, output_path)
            return True
        
        # If mute-only mode, use audio muting instead of cutting
        if mute_only:
            return self._mute_audio_segments(input_path, output_path, segments_to_remove)
        
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
                    original_bitrate: int = None, use_qsv_override: bool = None) -> bool:
        """Apply cuts using FFmpeg"""
        
        # Check for hardware acceleration support (VAAPI for Intel iGPU, or QSV)
        use_hw_accel = False
        hw_accel_type = None
        
        if use_qsv_override is not None:
            use_hw_accel = use_qsv_override
            hw_accel_type = 'qsv' if use_qsv_override else None
        else:
            # Try VAAPI first (more reliable for Intel iGPU)
            try:
                import os
                if os.path.exists('/dev/dri/renderD128'):
                    # Test VAAPI
                    result = subprocess.run(
                        ['ffmpeg', '-hide_banner', '-vaapi_device', '/dev/dri/renderD128', 
                         '-f', 'lavfi', '-i', 'nullsrc=s=64x64:d=0.1', 
                         '-vf', 'format=nv12,hwupload', '-c:v', 'h264_vaapi', 
                         '-f', 'null', '-'],
                        capture_output=True, timeout=5
                    )
                    if result.returncode == 0:
                        use_hw_accel = True
                        hw_accel_type = 'vaapi'
                        print("  ✓ Intel VAAPI hardware acceleration enabled (3-5x faster)")
            except:
                pass
            
            # Fallback to QSV if VAAPI failed
            if not use_hw_accel:
                try:
                    subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], 
                                 capture_output=True, check=True)
                    use_hw_accel = True
                    hw_accel_type = 'qsv'
                    print("  ✓ Intel Quick Sync Video (QSV) detected - attempting hardware acceleration")
                except:
                    print("  Hardware acceleration not available - using CPU encoding")

        # Show quality matching info if bitrate detected
        if original_bitrate:
            if original_bitrate < 200000:
                crf_value = 35
            elif original_bitrate < 500000:
                crf_value = 32
            elif original_bitrate < 1000000:
                crf_value = 28
            elif original_bitrate < 2000000:
                crf_value = 23
            else:
                crf_value = 18
            print(f"  Matching original video quality: {original_bitrate//1000}kbps (CRF {crf_value})")
        
        try:
            # Use filter_complex with concat for more reliable segment cutting
            if len(keep_segments) == 1:
                # Single segment - simple cut
                start, end = keep_segments[0]
                duration = end - start
                
                # Build FFmpeg command based on hardware acceleration type
                if hw_accel_type == 'vaapi':
                    cmd = [
                        'ffmpeg', '-vaapi_device', '/dev/dri/renderD128',
                        '-i', str(input_path),
                        '-ss', str(start),
                        '-t', str(duration),
                        '-vf', 'format=nv12,hwupload',
                        '-c:v', 'h264_vaapi',
                        '-qp', '24',  # Quality parameter for VAAPI
                        '-c:a', 'copy',
                        '-avoid_negative_ts', 'make_zero',
                        '-y', str(output_path)
                    ]
                elif hw_accel_type == 'qsv':
                    cmd = [
                        'ffmpeg', '-i', str(input_path),
                        '-ss', str(start),
                        '-t', str(duration),
                        '-c:v', 'h264_qsv',
                        '-preset', 'fast',
                        '-c:a', 'copy',
                        '-avoid_negative_ts', 'make_zero',
                        '-y', str(output_path)
                    ]
                else:
                    cmd = [
                        'ffmpeg', '-i', str(input_path),
                        '-ss', str(start),
                        '-t', str(duration),
                        '-c:v', 'libx264',
                        '-preset', 'fast',
                        '-c:a', 'copy',
                        '-avoid_negative_ts', 'make_zero',
                        '-y', str(output_path)
                    ]
                
                if not use_hw_accel:
                    # Match original video quality if bitrate detected
                    if original_bitrate:
                        # Estimate CRF based on original bitrate
                        # Lower bitrate = higher CRF (lower quality)
                        # Higher bitrate = lower CRF (higher quality)
                        # Rough mapping: 100kbps -> CRF 35, 500kbps -> CRF 23, 2000kbps -> CRF 18
                        if original_bitrate < 200000:  # < 200kbps
                            crf_value = 35
                        elif original_bitrate < 500000:  # < 500kbps
                            crf_value = 32
                        elif original_bitrate < 1000000:  # < 1Mbps
                            crf_value = 28
                        elif original_bitrate < 2000000:  # < 2Mbps
                            crf_value = 23
                        else:  # >= 2Mbps
                            crf_value = 18
                        cmd.extend(['-crf', str(crf_value), '-preset', 'fast'])
                    else:
                        # Fallback to CRF 23 if bitrate not detected
                        cmd.extend(['-crf', '23', '-preset', 'fast'])
                else:
                    # Force nv12 for QSV compatibility
                    if original_bitrate:
                        target_bitrate = int(original_bitrate * 1.1)
                        cmd.extend(['-vf', 'format=nv12', '-b:v', f'{target_bitrate}'])
                    else:
                        cmd.extend(['-vf', 'format=nv12', '-global_quality', '23'])

            else:
                # Multiple segments - extract each, then concat
                import tempfile
                temp_dir = Path(tempfile.mkdtemp())
                segment_files = []
                total_segments = len(keep_segments)
                
                print(f"  Extracting {total_segments} segments to keep...")
                for i, (start, end) in enumerate(keep_segments, 1):
                    duration = end - start
                    segment_file = temp_dir / f'segment_{i:04d}.mp4'
                    segment_files.append(segment_file)
                    
                    print(f"    Extracting segment {i}/{total_segments}: {start:.1f}s - {end:.1f}s ({duration:.1f}s)...", end='\r')
                    
                    # Extract segment with hardware acceleration
                    if hw_accel_type == 'vaapi':
                        extract_cmd = [
                            'ffmpeg', '-vaapi_device', '/dev/dri/renderD128',
                            '-i', str(input_path),
                            '-ss', str(start),
                            '-t', str(duration),
                            '-vf', 'format=nv12,hwupload',
                            '-c:v', 'h264_vaapi',
                            '-qp', '24',
                            '-c:a', 'aac',
                            '-b:a', '128k',
                            '-avoid_negative_ts', 'make_zero',
                        ]
                    elif hw_accel_type == 'qsv':
                        extract_cmd = [
                            'ffmpeg', '-i', str(input_path),
                            '-ss', str(start),
                            '-t', str(duration),
                            '-c:v', 'h264_qsv',
                            '-preset', 'fast',
                            '-c:a', 'aac',
                            '-b:a', '128k',
                            '-avoid_negative_ts', 'make_zero',
                        ]
                    else:
                        extract_cmd = [
                            'ffmpeg', '-i', str(input_path),
                            '-ss', str(start),
                            '-t', str(duration),
                            '-c:v', 'libx264',
                            '-preset', 'fast',
                            '-c:a', 'aac',
                            '-b:a', '128k',
                            '-avoid_negative_ts', 'make_zero',
                        ]
                        extract_cmd.extend(['-loglevel', 'error', '-y', str(segment_file)])
                    
                    if not use_hw_accel:
                        # Match original video quality if bitrate detected
                        if original_bitrate:
                            # Estimate CRF based on original bitrate (same logic as single segment)
                            if original_bitrate < 200000:  # < 200kbps
                                crf_value = 35
                            elif original_bitrate < 500000:  # < 500kbps
                                crf_value = 32
                            elif original_bitrate < 1000000:  # < 1Mbps
                                crf_value = 28
                            elif original_bitrate < 2000000:  # < 2Mbps
                                crf_value = 23
                            else:  # >= 2Mbps
                                crf_value = 18
                            extract_cmd.extend(['-crf', str(crf_value)])
                        else:
                            # Fallback to CRF 23 if bitrate not detected
                            extract_cmd.extend(['-crf', '23', '-preset', 'fast'])
                    # Hardware acceleration commands already have proper quality settings built-in

                    subprocess.run(extract_cmd, capture_output=True, check=True)
                
                print()  # New line after progress
                print(f"  ✓ All segments extracted")
                
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
            if use_hw_accel:
                print(f"  Warning: Hardware encoding failed. Retrying with CPU encoding...")
                # Retry with hardware acceleration forced off
                return self._apply_cuts(input_path, output_path, keep_segments, original_bitrate, use_qsv_override=False)
            
            print(f"  Error: FFmpeg failed")
            if e.stderr:
                error_msg = e.stderr if isinstance(e.stderr, str) else e.stderr.decode('utf-8', errors='ignore')
                print(f"  {error_msg[:1000]}")
            return False
        except Exception as e:
            if use_hw_accel:
                 print(f"  Warning: Error during hardware encoding ({e}). Retrying with CPU encoding...")
                 return self._apply_cuts(input_path, output_path, keep_segments, original_bitrate, use_qsv_override=False)

            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _mute_audio_segments(self, input_path: Path, output_path: Path,
                            segments_to_mute: List[Tuple[float, float]]) -> bool:
        """
        Mute audio in specified segments while keeping video intact.
        
        Args:
            input_path: Input video file
            output_path: Output video file
            segments_to_mute: List of (start, end) tuples to mute audio
            
        Returns:
            True if successful, False otherwise
        """
        print(f"  Processing {len(segments_to_mute)} segment(s) to mute...")
        
        # Get video duration
        duration = self._get_duration(input_path)
        if duration is None:
            print("  Error: Could not get video duration")
            return False
        
        # Build volume filter for FFmpeg
        # Format: volume=enable='between(t,start1,end1)+between(t,start2,end2)...':volume=0
        volume_conditions = []
        for start, end in segments_to_mute:
            # Clamp to video duration
            start = max(0, min(start, duration))
            end = max(0, min(end, duration))
            if start < end:
                volume_conditions.append(f"between(t,{start},{end})")
        
        if not volume_conditions:
            print("  Warning: No valid segments to mute - copying video as-is")
            import shutil
            shutil.copy2(input_path, output_path)
            return True
        
        # Create volume filter that mutes during specified segments
        enable_expr = '+'.join(volume_conditions)
        audio_filter = f"volume=enable='{enable_expr}':volume=0"
        
        # Process video with audio muting
        try:
            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-af', audio_filter,
                '-c:v', 'copy',  # Copy video without re-encoding
                '-c:a', 'aac',   # Re-encode audio (required for filter)
                '-b:a', '128k',  # Audio bitrate
                '-loglevel', 'error',
                '-y', str(output_path)
            ]
            
            print(f"  Applying audio muting filter...")
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"  ✓ Audio muting complete")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"  Error: FFmpeg audio muting failed")
            if e.stderr:
                error_msg = e.stderr if isinstance(e.stderr, str) else e.stderr.decode('utf-8', errors='ignore')
                print(f"  {error_msg[:1000]}")
            return False
        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            return False

