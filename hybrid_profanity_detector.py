"""
Hybrid profanity detector:
1) Use subtitles to find candidate cues quickly
2) Refine each candidate with short audio transcription for precise timestamps
3) Fall back to full-audio detection if subtitles yield no candidates
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Set, Tuple

from audio_profanity_detector_fast import AudioProfanityDetectorFast
from profanity_words import should_filter_word
from subtitle_processor import SubtitleProcessor
from timestamp_merger import TimestampMerger


class HybridProfanityDetector:
    """Subtitle-first detection with selective audio refinement."""

    def __init__(
        self,
        model_size: str = 'base',
        phrase_gap: float = 1.5,
        dialog_enhance: bool = True,
        profanity_words: Optional[Set[str]] = None,
        refine_pad: float = 1.0,
    ):
        self.model_size = model_size
        self.phrase_gap = phrase_gap
        self.dialog_enhance = dialog_enhance
        self.profanity_words = profanity_words
        self.refine_pad = max(0.0, refine_pad)
        self.subtitle_processor = SubtitleProcessor(profanity_words=profanity_words)
        self.audio_detector = AudioProfanityDetectorFast(
            model_size=model_size,
            phrase_gap=phrase_gap,
            dialog_enhance=dialog_enhance,
            auto_upgrade=False,
            profanity_words=profanity_words,
        )

    def detect(self, video_path: Path, subtitle_path: Path) -> List[Tuple[float, float, str]]:
        print("  Hybrid step 1: scanning subtitles for candidate profanity cues...")
        subtitle_segments = self.subtitle_processor.detect_profanity_segments(subtitle_path)
        if not subtitle_segments:
            print("  No subtitle candidates found. Falling back to full audio detection...")
            return self.audio_detector.detect(video_path)

        print(f"  Found {len(subtitle_segments)} subtitle candidate(s)")
        refined: List[Tuple[float, float, str]] = []
        for idx, (start, end, words) in enumerate(subtitle_segments, 1):
            window_start = max(0.0, start - self.refine_pad)
            window_end = end + self.refine_pad
            print(
                f"  Hybrid step 2 [{idx}/{len(subtitle_segments)}]: "
                f"refining {window_start:.2f}s-{window_end:.2f}s ('{words}')"
            )
            precise = self._refine_window(video_path, window_start, window_end)
            if precise:
                refined.extend(precise)
            else:
                # Keep subtitle cue if audio refinement finds nothing.
                refined.append((start, end, words))

        merger = TimestampMerger(merge_gap=self.phrase_gap)
        merged_ranges = merger.merge([], [(s, e) for s, e, _ in refined])
        # Re-attach labels for merged ranges.
        labeled: List[Tuple[float, float, str]] = []
        for m_start, m_end in merged_ranges:
            labels = []
            for s, e, word in refined:
                if s < m_end and e > m_start:
                    labels.append(word)
            label = ', '.join(sorted(set(', '.join(labels).split(', ')))) if labels else 'profanity'
            labeled.append((m_start, m_end, label))

        print(f"  ✓ Hybrid detection complete: {len(labeled)} segment(s)")
        return labeled

    def _refine_window(
        self,
        video_path: Path,
        start: float,
        end: float,
    ) -> List[Tuple[float, float, str]]:
        """Transcribe a short window and map word hits back to absolute timestamps."""
        if end <= start:
            return []

        temp_dir = Path(tempfile.mkdtemp())
        clip_path = temp_dir / 'window.wav'
        try:
            duration = max(0.05, end - start)
            cmd = [
                'ffmpeg', '-ss', f'{start:.3f}', '-i', str(video_path),
                '-t', f'{duration:.3f}',
                '-ar', '16000',
                '-ac', '1',
                '-loglevel', 'error',
                '-y', str(clip_path)
            ]
            subprocess.run(cmd, check=True, capture_output=True)

            segments, _info = self.audio_detector.whisper_model.transcribe(
                str(clip_path),
                **self.audio_detector._transcribe_kwargs(word_timestamps=True),
            )

            words = self.audio_detector.PROFANITY_WORDS
            hits: List[Tuple[float, float, str]] = []
            all_words = []
            for segment in segments:
                all_words.extend(getattr(segment, 'words', None) or [])

            for word_index, word_info in enumerate(all_words):
                token = word_info.word.strip().lower().rstrip('.,!?;:')
                context = self.audio_detector._word_context(all_words, word_index)
                if token in words and should_filter_word(token, context):
                    rel_start, rel_end = self.audio_detector._clamp_word_span(
                        float(word_info.start),
                        float(word_info.end),
                    )
                    abs_start = start + max(0.0, rel_start - 0.15)
                    abs_end = start + rel_end + 0.15
                    hits.append((abs_start, abs_end, token))
            return hits
        except Exception as e:
            print(f"    ⚠ Window refinement failed ({start:.2f}-{end:.2f}): {e}")
            return []
        finally:
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
