"""
Audio Profanity Detector (Faster-Whisper) - Detects profanity in audio using faster-whisper
"""

import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple

from profanity_words import PROFANITY_WORDS


class AudioProfanityDetectorFast:
    """Detects profanity in audio using faster-whisper with optional enhancements"""

    PROFANITY_WORDS = PROFANITY_WORDS

    _MODEL_ORDER = ['tiny', 'base', 'small', 'medium', 'large']

    def __init__(self,
                 model_size: str = 'tiny',
                 phrase_gap: float = 1.5,
                 dialog_enhance: bool = False,
                 dump_transcript_path: str = None,
                 min_wpm: float = 40.0,
                 auto_upgrade: bool = False):
        """Initialize audio profanity detector.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            phrase_gap: gap (s) to merge consecutive profanity words
            dialog_enhance: apply speech-focused filtering before transcription
            dump_transcript_path: write raw transcript words with timestamps
            min_wpm: warn if words per minute below threshold
            auto_upgrade: retry with next larger model once if WPM < min_wpm
        """
        self.model_size = model_size
        self.phrase_gap = phrase_gap
        self.dialog_enhance = dialog_enhance
        self.dump_transcript_path = dump_transcript_path
        self.min_wpm = min_wpm
        self.auto_upgrade = auto_upgrade
        self._upgraded_once = False
        self.whisper_model = None
        self._init_whisper()
    
    def _init_whisper(self):
        """Initialize faster-whisper model"""
        try:
            from faster_whisper import WhisperModel
            
            print(f"  Loading faster-whisper model: {self.model_size}...")
            # Try different compute types for CPU (int8_float16 first for best speed/accuracy balance)
            for compute_type in ['int8_float16', 'int8', 'float32']:
                try:
                    self.whisper_model = WhisperModel(self.model_size, device='cpu', compute_type=compute_type)
                    print(f"  ✓ Faster-whisper model loaded (compute_type={compute_type})")
                    break
                except ValueError:
                    continue
            
            if self.whisper_model is None:
                raise RuntimeError("Could not initialize faster-whisper with any compute type")
                
        except ImportError:
            raise ImportError(
                "faster-whisper not installed. Install with: pip install faster-whisper"
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
            print(f"  Transcribing audio with faster-whisper ({self.model_size} model)...")
            if duration:
                est_time = duration / 10  # faster-whisper is roughly 10x real-time on CPU
                print(f"  ⏳ Estimated time: ~{est_time:.1f} seconds for {duration/60:.1f} min video")
            
            import time
            start_time = time.time()
            
            segments, info = self.whisper_model.transcribe(
                str(audio_path),
                beam_size=5,
                word_timestamps=True,
                language='en'
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
            
            # Find profanity words
            print(f"  Searching {len(all_words)} words for profanity...")
            for word_info in all_words:
                word = word_info.word.strip().lower().rstrip('.,!?;:')
                if word in self.PROFANITY_WORDS:
                    start = word_info.start
                    end = word_info.end
                    padding = 0.15
                    profanity_segments.append((
                        max(0, start - padding),
                        end + padding,
                        word
                    ))
            
            print(f"  ✓ Profanity search complete: {len(profanity_segments)} profanity word(s) found")
            
            # Merge nearby profanity (within 1 second)
            if profanity_segments:
                print(f"  Merging nearby profanity segments...")
                profanity_segments = self._merge_nearby(profanity_segments)
                print(f"  ✓ Merged into {len(profanity_segments)} segment(s)")
        
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

    def _next_model(self, current: str):
        """Return next larger model name or None"""
        if current not in self._MODEL_ORDER:
            return None
        idx = self._MODEL_ORDER.index(current)
        if idx + 1 < len(self._MODEL_ORDER):
            return self._MODEL_ORDER[idx + 1]
        return None

    def _retry_transcribe(self, audio_path: Path):
        """Retry transcription after model upgrade, re-running profanity detection pipeline."""
        import time
        profanity_segments = []
        try:
            print(f"  ▶ Re-transcribing with upgraded model '{self.model_size}'...")
            start_time = time.time()
            segments, info = self.whisper_model.transcribe(
                str(audio_path),
                beam_size=5,
                word_timestamps=True,
                language='en'
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
            for word_info in all_words:
                word = word_info.word.strip().lower().rstrip('.,!?;:')
                if word in self.PROFANITY_WORDS:
                    start = word_info.start
                    end = word_info.end
                    padding = 0.15
                    profanity_segments.append((
                        max(0, start - padding),
                        end + padding,
                        word
                    ))
            print(f"  ✓ Profanity search complete: {len(profanity_segments)} profanity word(s) found")
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
