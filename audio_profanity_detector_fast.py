"""
Audio Profanity Detector (Faster-Whisper) - Detects profanity in audio using faster-whisper
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

from profanity_words import PROFANITY_WORDS, get_profanity_words


class MissingBinaryError(RuntimeError):
    """Raised when required system binaries (ffmpeg/ffprobe) are not available."""


class AudioProfanityDetectorFast:
    """Detects profanity in audio using faster-whisper with optional enhancements"""

    PROFANITY_WORDS = PROFANITY_WORDS
    
    # Common profanity phrases to detect as complete units
    PROFANITY_PHRASES = {
        'fuck you', 'fuck off', 'fuck this', 'fuck that', 'fuck me', 'fuck her', 'fuck him',
        'shit head', 'shit face', 'shit for brains', 'bull shit', 'bullshit',
        'ass hole', 'asshole', 'dumb ass', 'dumbass', 'smart ass', 'smartass',
        'son of a bitch', 'sonofabitch', 'mother fucker', 'motherfucker',
        'piece of shit', 'dick head', 'dickhead', 'cock sucker', 'cocksucker',
        'piss off', 'piss off', 'screw you', 'screw off'
    }

    _MODEL_ORDER = ['tiny', 'base', 'small', 'medium', 'large']

    # Pascal GPUs (e.g. Quadro P2000 / CC 6.1) lack useful FP16 Tensor Cores.
    # Prefer int8/float32 on CUDA; never rely on float16 there.
    _CUDA_COMPUTE_TYPES = ('int8', 'float32')
    _CPU_COMPUTE_TYPES = ('int8_float16', 'int8', 'float32')

    # Whisper sometimes stretches one word across a long silence, especially on
    # CPU without VAD. Cap single-word spans so clean dialogue is not removed.
    _MAX_SINGLE_WORD_DURATION = 1.0

    def __init__(self,
                 model_size: str = 'base',
                 phrase_gap: float = 1.5,
                 dialog_enhance: bool = False,
                 dump_transcript_path: str = None,
                 min_wpm: float = 40.0,
                 auto_upgrade: bool = False,
                 profanity_words=None,
                 include_religious: bool = False):
        """Initialize audio profanity detector."""
        self.model_size = model_size
        self.phrase_gap = phrase_gap
        self.dialog_enhance = dialog_enhance
        self.dump_transcript_path = dump_transcript_path
        self.min_wpm = min_wpm
        self.auto_upgrade = auto_upgrade
        self._upgraded_once = False
        self.whisper_model = None
        self.device = 'cpu'
        self.compute_type = None
        if profanity_words is not None:
            self.PROFANITY_WORDS = set(profanity_words)
        else:
            self.PROFANITY_WORDS = get_profanity_words(include_religious=include_religious)
        self._init_whisper()

    @staticmethod
    def _cuda_available() -> bool:
        """Return True only when CTranslate2 can see at least one CUDA device."""
        try:
            import ctranslate2
            return int(ctranslate2.get_cuda_device_count()) > 0
        except Exception:
            return False

    @staticmethod
    def _forced_device() -> Optional[str]:
        """
        Optional override: PROFANITY_FILTER_DEVICE=cpu|cuda
        Useful for debugging; invalid values are ignored.
        """
        forced = os.environ.get('PROFANITY_FILTER_DEVICE', '').strip().lower()
        if forced in ('cpu', 'cuda'):
            return forced
        return None

    def _devices_to_try(self) -> List[str]:
        forced = self._forced_device()
        if forced == 'cpu':
            return ['cpu']
        if forced == 'cuda':
            # Still fall back to CPU if forced CUDA load fails.
            return ['cuda', 'cpu']
        if self._cuda_available():
            return ['cuda', 'cpu']
        return ['cpu']

    @classmethod
    def _compute_types_for(cls, device: str) -> Tuple[str, ...]:
        if device == 'cuda':
            return cls._CUDA_COMPUTE_TYPES
        return cls._CPU_COMPUTE_TYPES

    def _try_load_model(self, WhisperModel, device: str):
        """Try compute types for a device. Returns (model, compute_type) or (None, None)."""
        last_error = None
        for compute_type in self._compute_types_for(device):
            try:
                model = WhisperModel(
                    self.model_size,
                    device=device,
                    compute_type=compute_type,
                )
                return model, compute_type
            except Exception as exc:
                last_error = exc
                print(f"  ⚠ {device}/{compute_type} unavailable: {exc}")
                continue
        if last_error is not None:
            print(f"  ⚠ Could not initialize model on {device}: {last_error}")
        return None, None

    def _init_whisper(self):
        """Initialize faster-whisper on GPU when available, otherwise CPU."""
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            raise ImportError(
                "faster-whisper not installed. Install with: pip install faster-whisper"
            )

        print(f"  Loading faster-whisper model: {self.model_size}...")

        forced = self._forced_device()
        if forced:
            print(f"  Device override via PROFANITY_FILTER_DEVICE={forced}")

        devices = self._devices_to_try()
        if devices[0] == 'cuda':
            print("  ✓ CUDA GPU detected — preferring GPU")
        else:
            print("  No CUDA GPU available — using CPU")

        self.whisper_model = None
        self.compute_type = None

        for device in devices:
            if device == 'cpu' and 'cuda' in devices:
                print("  Falling back to CPU...")

            model, compute_type = self._try_load_model(WhisperModel, device)
            if model is not None:
                self.whisper_model = model
                self.device = device
                self.compute_type = compute_type
                print(
                    f"  ✓ Faster-whisper model loaded on {device.upper()} "
                    f"(compute_type={compute_type})"
                )
                return

        raise RuntimeError(
            "Could not initialize faster-whisper on CUDA or CPU with any supported compute type"
        )
    
    def detect(self, video_path: Path) -> List[Tuple[float, float, str]]:
        """
        Detect profanity in audio.
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of (start_time, end_time, word) tuples for profanity segments
        """
        if not self.whisper_model:
            return []

        # Fail fast with a clear, actionable message instead of silently returning no detections.
        self._ensure_media_binaries()
        
        temp_dir = Path(tempfile.mkdtemp())
        profanity_segments = []
        
        try:
            # Get video duration
            try:
                duration_cmd = [
                    'ffprobe', '-v', 'error',
                    '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1',
                    str(video_path)
                ]
                duration_result = subprocess.run(duration_cmd, capture_output=True, text=True, check=True)
                duration = float(duration_result.stdout.strip())
                print(f"  Video duration: {duration/60:.1f} minutes")
            except:
                duration = None
            
            # Extract audio with optional dialog enhancement
            print(f"  Extracting audio from video{' (dialog enhance)' if self.dialog_enhance else ''}...")
            audio_path = temp_dir / 'audio.wav'
            filter_chain = None
            if self.dialog_enhance:
                # Emphasize vocal range, normalize dynamics, modest amplification
                filter_chain = 'highpass=f=200,lowpass=f=3500,dynaudnorm=f=75,volume=1.3'
            cmd = ['ffmpeg', '-i', str(video_path)]
            if filter_chain:
                cmd += ['-af', filter_chain]
            cmd += [
                '-ar', '16000',  # Whisper expects 16kHz
                '-ac', '1',       # Mono
                '-loglevel', 'error',
                '-y', str(audio_path)
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            print(f"  ✓ Audio extracted")
            
            # Transcribe with faster-whisper
            print(
                f"  Transcribing audio with faster-whisper "
                f"({self.model_size} on {self.device.upper()}, compute_type={self.compute_type})..."
            )
            if duration:
                # Rough real-time factors: GPU is typically much faster than CPU.
                realtime_factor = 30.0 if self.device == 'cuda' else 10.0
                est_time = duration / realtime_factor
                print(f"  ⏳ Estimated time: ~{est_time:.1f} seconds for {duration/60:.1f} min video")
            
            import time
            start_time = time.time()
            
            segments, info = self.whisper_model.transcribe(
                str(audio_path),
                **self._transcribe_kwargs(word_timestamps=True),
            )
            
            # Convert generator to list and get all words
            all_words = []
            for segment in segments:
                for word in segment.words:
                    all_words.append(word)
            
            elapsed = time.time() - start_time
            print(f"  ✓ Transcription complete in {elapsed:.1f}s ({info.duration/elapsed:.1f}x real-time)")

            # Words per minute diagnostic
            if info.duration and info.duration > 0:
                wpm = len(all_words) / (info.duration / 60.0)
                print(f"  Transcript stats: {len(all_words)} words, {wpm:.1f} WPM")
                if wpm < self.min_wpm:
                    print(f"  ⚠ Low WPM (<{self.min_wpm:.0f}) indicates under-transcription; audio may be complex or model too small.")
                    # Auto-upgrade logic (single retry)
                    if self.auto_upgrade and not self._upgraded_once:
                        next_model = self._next_model(self.model_size)
                        if next_model:
                            print(f"  ↻ Auto-upgrade enabled: retrying with larger model '{next_model}'...")
                            self.model_size = next_model
                            self._upgraded_once = True
                            self._init_whisper()  # reload model
                            return self._retry_transcribe(audio_path)
                        else:
                            print("  ℹ Already at largest model; cannot upgrade further.")

            # Dump transcript if requested
            if self.dump_transcript_path:
                try:
                    with open(self.dump_transcript_path, 'w') as f:
                        for w in all_words:
                            f.write(f"{w.start:.3f}\t{w.end:.3f}\t{w.word.strip()}\n")
                    print(f"  ✓ Raw transcript dumped to: {self.dump_transcript_path}")
                except Exception as e:
                    print(f"  ⚠ Failed to dump transcript: {e}")
            
            # Find profanity words and phrases
            print(f"  Searching {len(all_words)} words for profanity...")
            
            # First pass: detect individual profanity words
            for word_info in all_words:
                word = word_info.word.strip().lower().rstrip('.,!?;:')
                if word in self.PROFANITY_WORDS:
                    start, end = self._clamp_word_span(word_info.start, word_info.end)
                    padding = 0.15  # Match parent app padding (0.15s to catch partial sounds)
                    profanity_segments.append((
                        max(0, start - padding),
                        end + padding,
                        word
                    ))
            
            # Second pass: detect profanity phrases (2-word combinations)
            for i in range(len(all_words) - 1):
                word1_info = all_words[i]
                word2_info = all_words[i + 1]
                
                word1 = word1_info.word.strip().lower().rstrip('.,!?;:')
                word2 = word2_info.word.strip().lower().rstrip('.,!?;:')
                
                phrase = f"{word1} {word2}"
                if phrase in self.PROFANITY_PHRASES:
                    start = word1_info.start
                    end = word2_info.end
                    padding = 0.15  # Match parent app padding (0.15s to catch partial sounds)
                    profanity_segments.append((
                        max(0, start - padding),
                        end + padding,
                        phrase
                    ))
            
            # Third pass: Enhanced phrase detection - look for non-consecutive phrases
            # This catches cases where "fuck" and "you" might have gaps or be detected separately
            # Check if profanity word is followed by phrase completion words within phrase_gap
            phrase_completions = {
                'fuck': ['you', 'off', 'this', 'that', 'me', 'her', 'him'],
                'shit': ['head', 'face'],
                'ass': ['hole'],
                'dick': ['head'],
                'cock': ['sucker'],
                'piss': ['off'],
                'screw': ['you', 'off']
            }
            
            for i, word_info in enumerate(all_words):
                word = word_info.word.strip().lower().rstrip('.,!?;:')
                if word in phrase_completions:
                    # Look ahead for completion words within phrase_gap
                    for j in range(i + 1, min(i + 3, len(all_words))):  # Check up to 10 words ahead
                        next_word_info = all_words[j]
                        next_word = next_word_info.word.strip().lower().rstrip('.,!?;:')
                        
                        # Check if next word completes a phrase
                        if next_word in phrase_completions[word]:
                            # Check if within phrase_gap distance
                            time_gap = next_word_info.start - word_info.end
                            if time_gap <= 0.5:
                                # Found a phrase match - create segment covering both words
                                phrase = f"{word} {next_word}"
                                start = word_info.start
                                end = next_word_info.end
                                padding = 0.15  # Match parent app padding (0.15s to catch partial sounds)
                                profanity_segments.append((
                                    max(0, start - padding),
                                    end + padding,
                                    phrase
                                ))
                                break  # Found completion, move to next word
            
            print(f"  ✓ Profanity search complete: {len(profanity_segments)} profanity segment(s) found")
            
            # Merge nearby profanity (within 1 second)
            if profanity_segments:
                print(f"  Merging nearby profanity segments...")
                profanity_segments = self._merge_nearby(profanity_segments)
                print(f"  ✓ Merged into {len(profanity_segments)} segment(s)")
        
        except FileNotFoundError as e:
            raise MissingBinaryError(
                "Required media tool not found while running transcription pipeline. "
                "Please install FFmpeg (which includes ffmpeg and ffprobe) and ensure both are in PATH."
            ) from e
        except Exception as e:
            print(f"  ✗ Error during audio profanity detection: {e}")
            import traceback
            traceback.print_exc()
            profanity_segments = []
        finally:
            # Clean up temp directory
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        
        if not profanity_segments:
            print(f"  ⚠ No profanity segments detected or detection failed")
        else:
            print(f"  ✓ Successfully detected {len(profanity_segments)} profanity segment(s)")
        
        return profanity_segments

    def _ensure_media_binaries(self) -> None:
        """Verify ffmpeg and ffprobe are available in PATH."""
        missing = []
        if shutil.which('ffmpeg') is None:
            missing.append('ffmpeg')
        if shutil.which('ffprobe') is None:
            missing.append('ffprobe')
        if missing:
            raise MissingBinaryError(
                f"Missing required binary/binaries: {', '.join(missing)}. "
                "Install FFmpeg and make sure ffmpeg/ffprobe are available in your PATH."
            )

    def _next_model(self, current: str):
        """Return next larger model name or None"""
        if current not in self._MODEL_ORDER:
            return None
        idx = self._MODEL_ORDER.index(current)
        if idx + 1 < len(self._MODEL_ORDER):
            return self._MODEL_ORDER[idx + 1]
        return None

    @classmethod
    def _transcribe_kwargs(cls, word_timestamps: bool = True) -> dict:
        """
        Shared faster-whisper options.

        vad_filter skips long silences before alignment. Without it, CPU runs in
        particular can assign a single word a multi-second span across quiet gaps.
        """
        return {
            'beam_size': 5,
            'word_timestamps': word_timestamps,
            'language': 'en',
            'vad_filter': True,
        }

    @classmethod
    def _clamp_word_span(cls, start: float, end: float) -> Tuple[float, float]:
        """Keep the word end and pull an overstretched start forward."""
        if end <= start:
            return start, end
        max_dur = cls._MAX_SINGLE_WORD_DURATION
        if (end - start) > max_dur:
            start = end - max_dur
        return max(0.0, start), end

    def _retry_transcribe(self, audio_path: Path):
        """Retry transcription after model upgrade, re-running profanity detection pipeline."""
        import time
        profanity_segments = []
        try:
            print(f"  ▶ Re-transcribing with upgraded model '{self.model_size}'...")
            start_time = time.time()
            segments, info = self.whisper_model.transcribe(
                str(audio_path),
                **self._transcribe_kwargs(word_timestamps=True),
            )
            all_words = []
            for segment in segments:
                for word in segment.words:
                    all_words.append(word)
            elapsed = time.time() - start_time
            print(f"  ✓ Upgrade transcription complete in {elapsed:.1f}s ({info.duration/elapsed:.1f}x real-time)")
            wpm = len(all_words) / (info.duration / 60.0) if info.duration else 0
            print(f"  Transcript stats (upgraded): {len(all_words)} words, {wpm:.1f} WPM")
            if self.dump_transcript_path:
                try:
                    with open(self.dump_transcript_path, 'w') as f:
                        for w in all_words:
                            f.write(f"{w.start:.3f}\t{w.end:.3f}\t{w.word.strip()}\n")
                    print(f"  ✓ Raw transcript dumped to: {self.dump_transcript_path}")
                except Exception as e:
                    print(f"  ⚠ Failed to dump transcript: {e}")
            print(f"  Searching {len(all_words)} words for profanity...")
            
            # First pass: detect individual profanity words
            for word_info in all_words:
                word = word_info.word.strip().lower().rstrip('.,!?;:')
                if word in self.PROFANITY_WORDS:
                    start, end = self._clamp_word_span(word_info.start, word_info.end)
                    padding = 0.15  # Match parent app padding (0.15s to catch partial sounds)
                    profanity_segments.append((
                        max(0, start - padding),
                        end + padding,
                        word
                    ))
            
            # Second pass: detect profanity phrases (2-word combinations)
            for i in range(len(all_words) - 1):
                word1_info = all_words[i]
                word2_info = all_words[i + 1]
                
                word1 = word1_info.word.strip().lower().rstrip('.,!?;:')
                word2 = word2_info.word.strip().lower().rstrip('.,!?;:')
                
                phrase = f"{word1} {word2}"
                if phrase in self.PROFANITY_PHRASES:
                    start = word1_info.start
                    end = word2_info.end
                    padding = 0.15  # Match parent app padding (0.15s to catch partial sounds)
                    profanity_segments.append((
                        max(0, start - padding),
                        end + padding,
                        phrase
                    ))
            
            # Third pass: Enhanced phrase detection - look for nearby phrase completions
            # This catches cases where "fuck" and "you" might have a small gap (1-2 words max)
            # Only checks next 2 words ahead, not 10, since phrases like "fuck you" are adjacent
            phrase_completions = {
                'fuck': ['you', 'off', 'this', 'that', 'me', 'her', 'him'],
                'shit': ['head', 'face'],
                'ass': ['hole'],
                'dick': ['head'],
                'cock': ['sucker'],
                'piss': ['off'],
                'screw': ['you', 'off']
            }
            
            for i, word_info in enumerate(all_words):
                word = word_info.word.strip().lower().rstrip('.,!?;:')
                if word in phrase_completions:
                    # Look ahead only 1-2 words (not 10) since phrases are adjacent
                    for j in range(i + 1, min(i + 3, len(all_words))):  # Check next 2 words only
                        next_word_info = all_words[j]
                        next_word = next_word_info.word.strip().lower().rstrip('.,!?;:')
                        
                        # Check if next word completes a phrase
                        if next_word in phrase_completions[word]:
                            # Check if within reasonable time distance (0.5s for adjacent words)
                            time_gap = next_word_info.start - word_info.end
                            if time_gap <= 0.5:  # 0.5s max gap for adjacent phrase words
                                # Found a phrase match - create segment covering both words
                                phrase = f"{word} {next_word}"
                                start = word_info.start
                                end = next_word_info.end
                                padding = 0.15  # Match parent app padding (0.15s to catch partial sounds)
                                profanity_segments.append((
                                    max(0, start - padding),
                                    end + padding,
                                    phrase
                                ))
                                break  # Found completion, move to next word
            
            print(f"  ✓ Profanity search complete: {len(profanity_segments)} profanity segment(s) found")
            if profanity_segments:
                print(f"  Merging nearby profanity segments...")
                profanity_segments = self._merge_nearby(profanity_segments)
                print(f"  ✓ Merged into {len(profanity_segments)} segment(s)")
        except Exception as e:
            print(f"  ✗ Error during upgraded transcription: {e}")
        if not profanity_segments:
            print(f"  ⚠ No profanity segments detected or detection failed (upgraded run)")
        else:
            print(f"  ✓ Successfully detected {len(profanity_segments)} profanity segment(s) (upgraded)")
        return profanity_segments
    
    def _merge_nearby(self, segments: List[Tuple[float, float, str]]) -> List[Tuple[float, float, str]]:
        """Merge profanity segments that are close together
        
        Uses aggressive merging to catch split phrases like 'fuck you', 'shit head', etc.
        Since we only detect actual profanity words, consecutive profanity within 1.5s
        is almost certainly part of the same phrase.
        """
        if not segments:
            return []
        
        segments.sort(key=lambda x: x[0])
        merged = []
        current_start, current_end, current_words = segments[0]
        current_words_set = {current_words}
        
        for start, end, word in segments[1:]:
            # Aggressively merge consecutive profanity words within 1.5 seconds
            # This catches split phrases where Whisper detects words separately
            # e.g., "fuck" (79.76-80.08) + "you" (80.08-80.88) -> merge into one segment
            if start <= current_end + self.phrase_gap:
                current_end = max(current_end, end)
                current_words_set.add(word)
            else:
                merged.append((current_start, current_end, ', '.join(sorted(current_words_set))))
                current_start, current_end, current_words = start, end, word
                current_words_set = {word}
        
        merged.append((current_start, current_end, ', '.join(sorted(current_words_set))))
        return merged
