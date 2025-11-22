"""
Audio Profanity Detector - Detects profanity in audio using Whisper STT
"""

import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple

from profanity_words import PROFANITY_WORDS


class AudioProfanityDetector:
    """Detects profanity in audio using Whisper speech-to-text"""
    
    # Use shared profanity word list
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
        """Initialize Whisper model"""
        try:
            import warnings
            import whisper
            # Suppress FP16 warning on CPU (expected behavior)
            warnings.filterwarnings('ignore', message='FP16 is not supported on CPU')
            print(f"  Loading Whisper model: {self.model_size}...")
            self.whisper_model = whisper.load_model(self.model_size)
            print(f"  Whisper model loaded")
        except ImportError:
            raise ImportError(
                "Whisper not installed. Install with: pip install openai-whisper\n"
                "Note: Requires PyTorch (CPU version)"
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
            # Get video duration first
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
            
            # Transcribe with Whisper
            print(f"  Transcribing audio with Whisper ({self.model_size} model)...")
            if duration:
                print(f"  ⏳ This may take {duration/60*2:.1f}-{duration/60*5:.1f} minutes for {duration/60:.1f} min video...")
            else:
                print(f"  ⏳ This may take several minutes, please wait...")
            
            import warnings
            # Suppress FP16 warning during transcription (expected on CPU)
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', message='FP16 is not supported on CPU')
                result = self.whisper_model.transcribe(
                    str(audio_path),
                    word_timestamps=True,
                    language='en',
                    verbose=False  # Suppress Whisper's internal progress
                )
            
            print(f"  ✓ Transcription complete")
            
            # Count total words first
            total_words = 0
            for segment in result.get('segments', []):
                total_words += len(segment.get('words', []))
            
            # Find profanity words
            words_checked = 0
            for segment in result.get('segments', []):
                for word_info in segment.get('words', []):
                    words_checked += 1
                    word = word_info.get('word', '').strip().lower()
                    # Remove punctuation from end
                    word = word.rstrip('.,!?;:')
                    
                    # Check if word is profanity using EXACT match only (whole word)
                    # This prevents false positives like "house" matching "whore"
                    # or "hour" matching "whore"
                    if word in self.PROFANITY_WORDS:
                        start = word_info.get('start', 0)
                        end = word_info.get('end', 0)
                        # Add small padding around word
                        padding = 0.3
                        profanity_segments.append((
                            max(0, start - padding),
                            end + padding,
                            word
                        ))
                    
                    # Progress update every 1000 words
                    if words_checked % 1000 == 0:
                        print(f"    Checked {words_checked}/{total_words} words, found {len(profanity_segments)} profanity...", end='\r')
            
            print()  # New line after progress
            print(f"  ✓ Profanity search complete: {len(profanity_segments)} profanity word(s) found")
            
            # Merge nearby profanity (within 1 second)
            if profanity_segments:
                print(f"  Merging nearby profanity segments...")
                profanity_segments = self._merge_nearby(profanity_segments)
                print(f"  ✓ Merged into {len(profanity_segments)} segment(s)")
        
        except Exception as e:
            print(f"  ✗ Error during audio profanity detection: {e}")
            import traceback
            print(f"  Full error details:")
            traceback.print_exc()
            # Return empty list on error so processing can continue
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
        """Merge profanity segments that are close together"""
        if not segments:
            return []
        
        segments.sort(key=lambda x: x[0])
        merged = []
        current_start, current_end, current_words = segments[0]
        current_words_set = {current_words}
        
        for start, end, word in segments[1:]:
            # Merge if within 1 second
            if start <= current_end + 1.0:
                current_end = max(current_end, end)
                current_words_set.add(word)
            else:
                merged.append((current_start, current_end, ', '.join(sorted(current_words_set))))
                current_start, current_end, current_words = start, end, word
                current_words_set = {word}
        
        merged.append((current_start, current_end, ', '.join(sorted(current_words_set))))
        return merged

