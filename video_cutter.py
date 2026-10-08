"""
Video Cutter - Cuts out segments from video using FFmpeg

Goals:
- Prefer a single encode pass (no double re-encode)
- Keep cleaned file size near the source (source-aware bitrate / milder CRF)
- Preserve audio channels/sample rate/bitrate where possible
- Mute-only mode keeps original video bitstream via stream copy
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Removed _extract_single_segment_worker - using sequential extraction instead

class VideoCutter:
    """Cuts out segments from video using FFmpeg with quality-preserving encoding"""

    def __init__(self):
        self._selected_video_encoder = None
    
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

    # Cap each mute pass below FFmpeg's practical enable-expression limit
    # (~100 between()/ops in one volume filter on some builds). Also keeps
    # Windows command lines short. Values of 100-200 used to stay on the
    # single-pass path and could fail; chunking starts above this size.
    _MUTE_CHUNK_SIZE = 99

    def _mute_segments(self, input_path: Path, output_path: Path,
                       segments_to_mute: List[Tuple[float, float]]) -> bool:
        """Mute audio only in the provided time intervals while preserving video duration."""
        if not segments_to_mute:
            print("  No segments to mute - copying video as-is")
            import shutil
            shutil.copy2(input_path, output_path)
            return True

        audio_info = self._get_audio_stream_info(input_path)
        valid_segments = [(s, e) for s, e in segments_to_mute if e > s]
        if not valid_segments:
            print("  No valid mute intervals - copying video as-is")
            import shutil
            shutil.copy2(input_path, output_path)
            return True

        audio_encode_args = self._build_mute_audio_encode_args(
            audio_info, output_path.suffix.lower()
        )

        channels = audio_info.get('channels')
        layout = audio_info.get('channel_layout') or 'unknown'
        bitrate = audio_info.get('bit_rate')
        print(
            "  Audio profile: "
            f"channels={channels if channels else 'unknown'}, "
            f"layout={layout}, "
            f"bitrate={bitrate // 1000 if isinstance(bitrate, int) else 'unknown'}k"
        )

        # Small lists: one portable -af pass on the full file (fast path).
        if len(valid_segments) <= self._MUTE_CHUNK_SIZE:
            enable_expr = self._build_mute_enable_expr(valid_segments)
            audio_filter = f"volume=0:enable='{enable_expr}'"
            print(
                "  Mute encode: single-pass -af "
                f"({len(valid_segments)} interval(s); video copy; timeline unchanged)"
            )
            return self._mute_single_pass(
                input_path=input_path,
                output_path=output_path,
                audio_filter=audio_filter,
                audio_encode_args=audio_encode_args,
            )

        # Large lists: extract audio once, mute in chunked audio-only passes,
        # then mux muted audio back. Avoids huge CLI filters and MKV filter issues.
        print(
            f"  Mute encode: chunked audio-only passes "
            f"({len(valid_segments)} intervals, chunk size {self._MUTE_CHUNK_SIZE})"
        )
        return self._mute_segments_chunked_audio(
            input_path=input_path,
            output_path=output_path,
            segments_to_mute=valid_segments,
            audio_info=audio_info,
            audio_encode_args=audio_encode_args,
        )

    def _mute_single_pass(
        self,
        input_path: Path,
        output_path: Path,
        audio_filter: str,
        audio_encode_args: List[str],
    ) -> bool:
        """Mute with one portable -af pass while copying video/subtitle streams."""
        try:
            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-map', '0:v:0?',
                '-map', '0:a:0?',
                '-map', '0:s?',
                '-c:v', 'copy',
                '-c:s', 'copy',
                '-af', audio_filter,
                *audio_encode_args,
                *self._mute_container_args(output_path),
                '-loglevel', 'error',
                '-y', str(output_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("  ✓ Audio muting complete")
                return True

            print("  ⚠ Mute with subtitle copy failed; retrying without subtitle streams...")
            cmd_no_subs = [
                'ffmpeg', '-i', str(input_path),
                '-map', '0:v:0?',
                '-map', '0:a:0?',
                '-c:v', 'copy',
                '-af', audio_filter,
                *audio_encode_args,
                *self._mute_container_args(output_path),
                '-loglevel', 'error',
                '-y', str(output_path)
            ]
            result = subprocess.run(cmd_no_subs, capture_output=True, text=True)
            if result.returncode == 0:
                print("  ✓ Audio muting complete (subtitle streams not copied)")
                return True

            print("  ✗ FFmpeg mute command failed. Return code:", result.returncode)
            if result.stderr:
                err_lines = [l for l in result.stderr.splitlines() if l.strip()]
                print("    " + '\n    '.join(err_lines[:12]))
            return False
        except Exception as e:
            print(f"  Error during mute-only processing: {e}")
            return False

    def _mute_segments_chunked_audio(
        self,
        input_path: Path,
        output_path: Path,
        segments_to_mute: List[Tuple[float, float]],
        audio_info: Dict[str, Optional[object]],
        audio_encode_args: List[str],
    ) -> bool:
        """
        Large mute lists:
        1) extract primary audio once to a temp WAV
        2) apply mute filters in chunked audio-only passes
        3) mux muted audio onto original video (video stream copied)
        Temp files stay in the system temp directory, never the output folder.
        """
        import shutil

        temp_dir = Path(tempfile.mkdtemp(prefix='profanity_mute_'))
        try:
            extracted = temp_dir / 'source_audio.wav'
            if not self._extract_primary_audio_wav(input_path, extracted, audio_info):
                return False

            chunks = [
                segments_to_mute[i:i + self._MUTE_CHUNK_SIZE]
                for i in range(0, len(segments_to_mute), self._MUTE_CHUNK_SIZE)
            ]
            current_audio = extracted
            for idx, chunk in enumerate(chunks, 1):
                enable_expr = self._build_mute_enable_expr(chunk)
                audio_filter = f"volume=0:enable='{enable_expr}'"
                next_audio = temp_dir / f'muted_pass_{idx:03d}.wav'
                print(
                    f"  Mute pass {idx}/{len(chunks)}: "
                    f"{len(chunk)} interval(s) on audio-only track..."
                )
                cmd = [
                    'ffmpeg', '-i', str(current_audio),
                    '-af', audio_filter,
                    '-c:a', 'pcm_s16le',
                    '-loglevel', 'error',
                    '-y', str(next_audio)
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"  ✗ Audio mute pass {idx} failed. Return code:", result.returncode)
                    if result.stderr:
                        err_lines = [l for l in result.stderr.splitlines() if l.strip()]
                        print("    " + '\n    '.join(err_lines[:12]))
                    return False
                current_audio = next_audio

            print("  Combining muted audio with original video...")
            return self._mux_muted_audio(
                input_path=input_path,
                muted_audio_path=current_audio,
                output_path=output_path,
                audio_encode_args=audio_encode_args,
            )
        except Exception as e:
            print(f"  Error during chunked mute-only processing: {e}")
            return False
        finally:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

    def _extract_primary_audio_wav(
        self,
        input_path: Path,
        output_wav: Path,
        audio_info: Dict[str, Optional[object]],
    ) -> bool:
        """Extract primary audio to PCM WAV for lossless multi-pass muting."""
        cmd = [
            'ffmpeg', '-i', str(input_path),
            '-map', '0:a:0',
            '-vn',
            '-c:a', 'pcm_s16le',
        ]
        channels = audio_info.get('channels')
        if isinstance(channels, int) and channels > 0:
            cmd.extend(['-ac', str(channels)])
        sample_rate = audio_info.get('sample_rate')
        if isinstance(sample_rate, int) and sample_rate > 0:
            cmd.extend(['-ar', str(sample_rate)])
        cmd.extend(['-loglevel', 'error', '-y', str(output_wav)])

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("  ✗ Failed to extract audio for chunked mute. Return code:", result.returncode)
            if result.stderr:
                err_lines = [l for l in result.stderr.splitlines() if l.strip()]
                print("    " + '\n    '.join(err_lines[:12]))
            return False
        print("  ✓ Primary audio extracted for chunked mute processing")
        return True

    def _mux_muted_audio(
        self,
        input_path: Path,
        muted_audio_path: Path,
        output_path: Path,
        audio_encode_args: List[str],
    ) -> bool:
        """Replace primary audio with muted track; keep original video timeline."""
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-i', str(muted_audio_path),
            '-map', '0:v:0?',
            '-map', '1:a:0',
            '-map', '0:s?',
            '-c:v', 'copy',
            '-c:s', 'copy',
            *audio_encode_args,
            *self._mute_container_args(output_path),
            '-loglevel', 'error',
            '-y', str(output_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✓ Audio muting complete")
            return True

        print("  ⚠ Mux with subtitle copy failed; retrying without subtitle streams...")
        cmd_no_subs = [
            'ffmpeg',
            '-i', str(input_path),
            '-i', str(muted_audio_path),
            '-map', '0:v:0?',
            '-map', '1:a:0',
            '-c:v', 'copy',
            *audio_encode_args,
            *self._mute_container_args(output_path),
            '-loglevel', 'error',
            '-y', str(output_path)
        ]
        result = subprocess.run(cmd_no_subs, capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✓ Audio muting complete (subtitle streams not copied)")
            return True

        print("  ✗ Failed to mux muted audio. Return code:", result.returncode)
        if result.stderr:
            err_lines = [l for l in result.stderr.splitlines() if l.strip()]
            print("    " + '\n    '.join(err_lines[:12]))
        return False

    def _build_mute_enable_expr(self, segments: List[Tuple[float, float]]) -> str:
        """Build a compact enable expression for volume mute intervals."""
        parts = []
        for start, end in segments:
            if end <= start:
                continue
            parts.append(f"between(t,{start:.3f},{end:.3f})")
        return "+".join(parts)

    def _mute_container_args(self, output_path: Path) -> List[str]:
        """Container-specific mux flags for mute-only output."""
        if output_path.suffix.lower() == '.mp4':
            return ['-movflags', '+faststart']
        return []

    def _build_mute_audio_encode_args(
        self,
        audio_info: Dict[str, Optional[object]],
        container_suffix: str,
    ) -> List[str]:
        """
        Choose mute audio codec for A/V lock with stream-copied video.

        MP4: AAC (edit lists keep sync; matches prior behavior).
        MKV/WebM: FLAC (lossless, no AAC priming skew; verified vs tone timing).
        """
        suffix = (container_suffix or '').lower()
        channels = audio_info.get('channels')
        sample_rate = audio_info.get('sample_rate')

        if suffix in {'.mkv', '.webm'}:
            args = ['-c:a', 'flac']
            if isinstance(channels, int) and channels > 0:
                args.extend(['-ac', str(channels)])
            if isinstance(sample_rate, int) and sample_rate > 0:
                args.extend(['-ar', str(sample_rate)])
            return args

        # Default / MP4 / MOV: AAC
        return self._build_audio_encode_args(audio_info)

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
    
    def _get_video_bitrate(self, video_path: Path) -> Optional[int]:
        """Best-effort video bitrate in bps (stream, then format fallback)."""
        def _parse_bps(raw: str) -> Optional[int]:
            value = (raw or '').strip()
            if not value or value.upper() == 'N/A':
                return None
            try:
                bps = int(float(value))
            except ValueError:
                return None
            return bps if bps > 0 else None

        try:
            cmd = [
                'ffprobe', '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=bit_rate',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(video_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            stream_bps = _parse_bps(result.stdout)
            if stream_bps:
                return stream_bps
        except Exception:
            pass

        # Many MP4/MKV files omit per-stream bit_rate; estimate from container.
        try:
            cmd = [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=bit_rate:stream=bit_rate,codec_type',
                '-of', 'json',
                str(video_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            payload = json.loads(result.stdout or '{}')
            format_bps = _parse_bps(str((payload.get('format') or {}).get('bit_rate') or ''))
            audio_bps = 0
            for stream in payload.get('streams') or []:
                if stream.get('codec_type') == 'audio':
                    abps = _parse_bps(str(stream.get('bit_rate') or ''))
                    if abps:
                        audio_bps += abps
            if format_bps:
                estimated = format_bps - audio_bps
                if estimated > 100000:
                    return estimated
                return format_bps
        except Exception:
            pass
        return None

    def _target_video_bitrate(self, original_bitrate: Optional[int]) -> int:
        """Target output video bitrate near the source (avoid unconstrained encode)."""
        if original_bitrate and original_bitrate > 0:
            # Keep a sane floor/ceiling so tiny/huge probes do not break encoders.
            return max(300000, min(int(original_bitrate), 40000000))
        return 2500000

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
    
    def _choose_crf(self, original_bitrate: Optional[int]) -> int:
        """
        Pick a size-aware CRF (higher = smaller file).
        Tuned to stay near source size instead of near-lossless bloat.
        """
        if not original_bitrate:
            return 23
        if original_bitrate < 500000:
            return 23
        if original_bitrate < 2000000:
            return 20
        return 18

    def _choose_nvenc_cq(self, original_bitrate: Optional[int]) -> int:
        """NVENC CQ roughly aligned with the CPU CRF ladder."""
        return self._choose_crf(original_bitrate)

    def _has_audio_stream(self, audio_info: Dict[str, Optional[object]]) -> bool:
        codec = audio_info.get('codec_name')
        channels = audio_info.get('channels')
        if isinstance(codec, str) and codec.strip():
            return True
        return isinstance(channels, int) and channels > 0

    @staticmethod
    def _cpu_video_args(crf_value: int) -> List[str]:
        """CPU fallback: size-aware CRF with a fast preset (closer to pre-NVENC behavior)."""
        return [
            '-c:v', 'libx264',
            '-crf', str(crf_value),
            '-preset', 'veryfast',
            '-pix_fmt', 'yuv420p',
            '-threads', '0',
        ]

    def _hardware_encoder_candidates(
        self,
        original_bitrate: Optional[int],
    ) -> List[Tuple[str, List[str]]]:
        """
        Hardware H.264 encoders ordered by common availability.

        Bitrate is capped to the source so cleaned files stay near original size.
        Each candidate is validated with a real one-frame encode before use.
        """
        target = self._target_video_bitrate(original_bitrate)
        maxrate = int(target * 1.3)
        bufsize = int(target * 2)
        cq = self._choose_nvenc_cq(original_bitrate)
        # QSV quality numbers: higher = smaller file.
        qsv_quality = max(18, min(cq + 2, 28))
        vt_quality = max(50, min(75, 95 - cq))  # VideoToolbox: higher q = better

        return [
            (
                'NVIDIA NVENC',
                [
                    '-c:v', 'h264_nvenc',
                    '-preset', 'p5',
                    '-tune', 'hq',
                    '-rc', 'vbr',
                    '-cq', str(cq),
                    '-b:v', str(target),
                    '-maxrate', str(maxrate),
                    '-bufsize', str(bufsize),
                    '-profile:v', 'high',
                    '-pix_fmt', 'yuv420p',
                ],
            ),
            (
                'Intel Quick Sync',
                [
                    '-c:v', 'h264_qsv',
                    '-preset', 'medium',
                    '-global_quality', str(qsv_quality),
                    '-b:v', str(target),
                    '-maxrate', str(maxrate),
                    '-bufsize', str(bufsize),
                    '-pix_fmt', 'nv12',
                ],
            ),
            (
                'AMD AMF',
                [
                    '-c:v', 'h264_amf',
                    '-quality', 'balanced',
                    '-rc', 'vbr_peak',
                    '-b:v', str(target),
                    '-maxrate', str(maxrate),
                    '-bufsize', str(bufsize),
                    '-pix_fmt', 'yuv420p',
                ],
            ),
            (
                'Apple VideoToolbox',
                [
                    '-c:v', 'h264_videotoolbox',
                    '-b:v', str(target),
                    '-maxrate', str(maxrate),
                    '-bufsize', str(bufsize),
                    '-q:v', str(vt_quality),
                    '-pix_fmt', 'yuv420p',
                ],
            ),
        ]

    @staticmethod
    def _encoder_probe_succeeds(video_args: List[str]) -> bool:
        """Perform a real hardware encode probe instead of trusting FFmpeg's list."""
        cmd = [
            'ffmpeg',
            '-hide_banner',
            '-loglevel', 'error',
            '-f', 'lavfi',
            '-i', 'color=c=black:s=128x128:r=24',
            '-frames:v', '1',
            *video_args,
            '-f', 'null',
            '-',
        ]
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=20,
                check=False,
            )
            return result.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False

    def _select_video_encoder(
        self,
        crf_value: int,
        original_bitrate: Optional[int] = None,
    ) -> Tuple[str, List[str], bool]:
        """
        Select a working GPU encoder, with an explicit CPU-only override.

        PROFANITY_FILTER_VIDEO_ENCODER=cpu disables hardware encoding.
        """
        if self._selected_video_encoder is not None:
            name, args, hardware = self._selected_video_encoder
            if hardware:
                return name, list(args), hardware
            return name, self._cpu_video_args(crf_value), hardware

        forced = os.environ.get(
            'PROFANITY_FILTER_VIDEO_ENCODER',
            'auto',
        ).strip().lower()

        if forced != 'cpu':
            for name, args in self._hardware_encoder_candidates(original_bitrate):
                encoder_name = args[1]
                if forced not in ('', 'auto') and forced not in (
                    encoder_name.lower(),
                    name.lower(),
                ):
                    continue
                if self._encoder_probe_succeeds(args):
                    self._selected_video_encoder = (name, list(args), True)
                    return name, list(args), True

            if forced not in ('', 'auto'):
                print(
                    f"  ⚠ Requested video encoder '{forced}' is unavailable; "
                    "falling back to CPU"
                )

        self._selected_video_encoder = ('CPU libx264', [], False)
        return 'CPU libx264', self._cpu_video_args(crf_value), False

    def _apply_cuts(self, input_path: Path, output_path: Path,
                    keep_segments: List[Tuple[float, float]],
                    original_bitrate: int = None) -> bool:
        """Apply cuts with a single size-aware encode pass."""
        if not keep_segments:
            return False

        crf_value = self._choose_crf(original_bitrate)
        audio_info = self._get_audio_stream_info(input_path)
        has_audio = self._has_audio_stream(audio_info)
        audio_encode_args = self._build_audio_encode_args(audio_info) if has_audio else []
        encoder_name, video_args, hardware_encode = self._select_video_encoder(
            crf_value,
            original_bitrate,
        )
        target_bps = self._target_video_bitrate(original_bitrate)
        source_rate = f"~{target_bps // 1000}kbps target"
        if hardware_encode:
            print(
                f"  ✓ GPU video encoding enabled: {encoder_name} "
                f"(source-matched bitrate, {source_rate}, single pass)"
            )
        else:
            print(
                f"  No compatible GPU video encoder found — using CPU libx264 "
                f"(CRF {crf_value}, preset veryfast, {source_rate}, single pass)"
            )

        try:
            # Single keep-range: accurate trim + one encode (no concat).
            if len(keep_segments) == 1:
                start, end = keep_segments[0]
                duration = max(0.0, end - start)
                cmd = [
                    'ffmpeg', '-hide_banner',
                    '-i', str(input_path),
                    '-ss', f'{start:.3f}',
                    '-t', f'{duration:.3f}',
                    *video_args,
                ]
                if has_audio:
                    cmd.extend(audio_encode_args)
                else:
                    cmd.extend(['-an'])
                cmd.extend(['-avoid_negative_ts', 'make_zero', '-y', str(output_path)])
                print(
                    f"  [SIZE-AWARE] Single-segment encode via {encoder_name}"
                )
                result = subprocess.run(cmd, capture_output=True, text=True)
            else:
                # Multi-segment: one filter_complex pass (avoid extract+concat double encode).
                filter_parts = []
                concat_labels = []
                for i, (start, end) in enumerate(keep_segments):
                    if has_audio:
                        filter_parts.append(
                            f"[0:v]trim=start={start:.3f}:end={end:.3f},setpts=PTS-STARTPTS[v{i}];"
                            f"[0:a]atrim=start={start:.3f}:end={end:.3f},asetpts=PTS-STARTPTS[a{i}]"
                        )
                        concat_labels.append(f"[v{i}][a{i}]")
                    else:
                        filter_parts.append(
                            f"[0:v]trim=start={start:.3f}:end={end:.3f},setpts=PTS-STARTPTS[v{i}]"
                        )
                        concat_labels.append(f"[v{i}]")

                n = len(keep_segments)
                if has_audio:
                    filter_complex = (
                        ";".join(filter_parts)
                        + ";"
                        + "".join(concat_labels)
                        + f"concat=n={n}:v=1:a=1[outv][outa]"
                    )
                    map_args = ['-map', '[outv]', '-map', '[outa]', *video_args, *audio_encode_args]
                else:
                    filter_complex = (
                        ";".join(filter_parts)
                        + ";"
                        + "".join(concat_labels)
                        + f"concat=n={n}:v=1:a=0[outv]"
                    )
                    map_args = ['-map', '[outv]', *video_args, '-an']

                cmd = [
                    'ffmpeg', '-hide_banner',
                    '-i', str(input_path),
                    '-filter_complex', filter_complex,
                    *map_args,
                ]
                cmd.extend(['-y', str(output_path)])
                print(
                    f"  [SIZE-AWARE] Multi-segment single-pass encode "
                    f"({n} keep ranges, {encoder_name}, no double re-encode)"
                )
                result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0 and hardware_encode:
                print(
                    f"  ⚠ {encoder_name} failed for this video; "
                    "retrying safely with CPU libx264"
                )
                self._selected_video_encoder = ('CPU libx264', [], False)
                return self._apply_cuts(
                    input_path,
                    output_path,
                    keep_segments,
                    original_bitrate,
                )

            if result.returncode == 0:
                print("  ✓ Video cutting complete")
                return True

            print("  ✗ FFmpeg command failed. Return code:", result.returncode)
            if result.stderr:
                err_lines = [l for l in result.stderr.splitlines() if l.strip()]
                print("    " + '\n    '.join(err_lines[:12]))
            return False

        except subprocess.CalledProcessError as e:
            print("  Error: FFmpeg failed")
            stderr = e.stderr if isinstance(e.stderr, str) else (
                e.stderr.decode('utf-8', errors='ignore') if e.stderr else ''
            )
            if stderr:
                print("  " + "\n  ".join(stderr.splitlines()[:12]))
            return False
        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            return False

