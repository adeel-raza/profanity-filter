"""
Audio Profanity Detector (Faster-Whisper) - Detects profanity in audio using faster-whisper
"""

import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple

from profanity_words import PROFANITY_WORDS


class AudioProfanityDetectorFast:
    """Detects profanity in audio using faster-whisper"""
    
    PROFANITY_WORDS = PROFANITY_WORDS
    
    def __init__(self, model_size: str = 'tiny'):
        """
        Initialize audio profanity detector.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.whisper_model = None
        self._init_whisper()
    
    def _init_whisper(self):
        """Initialize faster-whisper model"""
        try:
            from faster_whisper import WhisperModel
            
            print(f"  Loading faster-whisper model: {self.model_size}...")
            # Try different compute types for CPU
            for compute_type in ['int8', 'int8_float16', 'float32']:
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
            
            # Extract audio
            print(f"  Extracting audio from video...")
            audio_path = temp_dir / 'audio.wav'
            cmd = [
                'ffmpeg', '-i', str(video_path),
                '-ar', '16000',  # Whisper expects 16kHz
                '-ac', '1',  # Mono
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
            
            # Find profanity words
            print(f"  Searching {len(all_words)} words for profanity...")
            for word_info in all_words:
                word = word_info.word.strip().lower()
                word = word.rstrip('.,!?;:')
                
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
            if start <= current_end + 1.5:
                current_end = max(current_end, end)
                current_words_set.add(word)
            else:
                merged.append((current_start, current_end, ', '.join(sorted(current_words_set))))
                current_start, current_end, current_words = start, end, word
                current_words_set = {word}
        
        merged.append((current_start, current_end, ', '.join(sorted(current_words_set))))
        return merged
