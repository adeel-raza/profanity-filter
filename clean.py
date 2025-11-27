#!/usr/bin/env python3
"""
Automated Movie Cleaner - Removes profanity from audio and subtitles
Usage: python clean.py input.mp4 output.mp4
"""

import argparse
import sys
import os

# Ensure unbuffered output for real-time verbose display
os.environ['PYTHONUNBUFFERED'] = '1'
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
from pathlib import Path
from typing import List, Tuple

from audio_profanity_detector_fast import AudioProfanityDetectorFast
from video_cutter import VideoCutter
from timestamp_merger import TimestampMerger
from subtitle_processor import SubtitleProcessor
from generate_subtitles import generate_subtitles


def main():
    parser = argparse.ArgumentParser(
        description='Automatically remove profanity from videos using AI transcription'
    )
    parser.add_argument('input', type=str, help='Input video file (MP4, MKV, etc.)')
    parser.add_argument('output', type=str, nargs='?', default=None,
                       help='Output cleaned video file (optional - defaults to input_cleaned.ext)')
    parser.add_argument('--subs', type=str, default=None,
                       help='Use existing subtitle file instead of transcribing audio (SRT or VTT format)')
    parser.add_argument('--model', type=str, default='tiny',
                       help='Whisper model size: tiny (fastest), base, small, medium, large (most accurate). Default: tiny')
    parser.add_argument('--mute-only', action='store_true',
                       help='Mute audio during profanity instead of cutting segments (keeps video length unchanged)')
    parser.add_argument('--remove-timestamps', type=str, default=None,
                       help='Manually specify additional timestamps to remove (format: "start-end,start-end" e.g., "6-11,23-30")')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    # Auto-generate output filename if not provided
    if args.output:
        output_path = Path(args.output)
    else:
        # Generate output filename: input_cleaned.ext
        output_path = input_path.parent / f"{input_path.stem}_cleaned{input_path.suffix}"
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    # Check for subtitle file only if explicitly provided
    subtitle_input = None
    if args.subs:
        subtitle_input = Path(args.subs)
        if not subtitle_input.exists():
            print(f"Warning: Subtitle file not found: {subtitle_input}")
            print(f"Falling back to audio transcription...")
            subtitle_input = None
    
    print("=" * 60)
    print("AUTOMATED MOVIE CLEANER - PROFANITY FILTER")
    print("=" * 60)
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    subtitle_processor = SubtitleProcessor() if subtitle_input else None
    if subtitle_input:
        print(f"Subtitles: {subtitle_input} (will be processed after video cutting)")
    print()
    
    # Step 1: Detect profanity using AI transcription (faster-whisper)
    # Uses word-level timestamps for precise, accurate profanity removal
    audio_segments = []
    
    if subtitle_input:
        print("Step 1: Using provided subtitle file for profanity detection")
        print("-" * 60)
        print("Step 1a: Detecting profanity from subtitles...")
        if subtitle_processor:
            subtitle_segments = subtitle_processor.detect_profanity_segments(subtitle_input)
            if subtitle_segments:
                print(f"  ✓ Found {len(subtitle_segments)} subtitle-based segment(s) to remove")
                for start, end, words in subtitle_segments:
                    print(f"    - {start:.2f}s to {end:.2f}s: '{words}'")
                audio_segments = subtitle_segments
            else:
                print("  ⚠ No profanity segments detected from subtitles")
        print("-" * 60)
        print()
    else:
        print("Step 1: Transcribing audio and detecting profanity (faster-whisper)")
        print("-" * 60)
        try:
            audio_detector = AudioProfanityDetectorFast(model_size=args.model)
            audio_segments = audio_detector.detect(input_path)
            print("-" * 60)
            print(f"Step 1 Summary: Found {len(audio_segments)} profanity segment(s) in audio")
            if audio_segments:
                for start, end, word in audio_segments:
                    print(f"    - {start:.2f}s to {end:.2f}s ({end-start:.2f}s): '{word}'")
            else:
                print("    ✓ No profanity detected in audio")
            print()
        except Exception as e:
            print(f"  ✗ ERROR: Audio profanity detection failed: {e}")
            import traceback
            traceback.print_exc()
            print(f"  Continuing without audio profanity detection...")
            print()
            audio_segments = []
    
    
    # Step 2: Add manual timestamps if specified
    manual_segments = []
    if args.remove_timestamps:
        print("Step 2a: Processing manual timestamps...")
        for ts_pair in args.remove_timestamps.split(','):
            try:
                start_str, end_str = ts_pair.strip().split('-')
                start = float(start_str.strip())
                end = float(end_str.strip())
                manual_segments.append((start, end))
                print(f"  Added manual segment: {start:.2f}s to {end:.2f}s")
            except ValueError:
                print(f"  Warning: Invalid timestamp format: {ts_pair}")
        print()
    
    # Step 2: Merge segments (matches Hugging Face Gradio app exactly)
    print("Step 2: Merging segments...")
    print(f"  Audio segments: {len(audio_segments)}")
    merger = TimestampMerger()
    all_segments = []
    
    # Use audio segments (word-level timestamps from Whisper)
    # This matches the Gradio app which uses ONLY audio transcription
    if audio_segments:
        # Convert audio segments from (start, end, word) to (start, end)
        audio_segments_tuples = [(start, end) for start, end, word in audio_segments]
        all_segments = merger.merge(all_segments, audio_segments_tuples, padding=0.0, merge_gap=0.0)
        print(f"  Merged into {len(all_segments)} segment(s) to remove")
    
    # Add manual segments if specified
    if manual_segments:
        print(f"  Manual segments: {len(manual_segments)}")
        all_segments = merger.merge(all_segments, manual_segments, padding=0.05, merge_gap=0.0)
        print(f"  Total after manual: {len(all_segments)} segment(s) to remove")
    if all_segments:
        for i, (start, end) in enumerate(all_segments, 1):
            print(f"    {i}. {start:.2f}s to {end:.2f}s ({end-start:.2f}s)")
    else:
        print("    WARNING: No segments to remove!")
    print()
    
    if not all_segments:
        print("No profanity detected. Copying video as-is...")
        import shutil
        shutil.copy2(input_path, output_path)
        print(f"Output saved to: {output_path}")
        
        # Process subtitles to remove profanity words even if no video cuts needed
        if subtitle_input:
            output_base = output_path.stem
            output_dir = output_path.parent
            if subtitle_input.suffix.lower() == '.srt':
                output_subtitle = output_dir / f"{output_base}.srt"
            elif subtitle_input.suffix.lower() == '.vtt':
                output_subtitle = output_dir / f"{output_base}.vtt"
            else:
                output_subtitle = output_dir / f"{output_base}{subtitle_input.suffix}"
            
            # Process subtitles to filter profanity words
            subtitle_processor = SubtitleProcessor()
            if subtitle_input.suffix.lower() == '.srt':
                subtitle_processor.process_srt(subtitle_input, output_subtitle, [])
            elif subtitle_input.suffix.lower() == '.vtt':
                subtitle_processor.process_vtt(subtitle_input, output_subtitle, [])
            else:
                subtitle_processor.process_srt(subtitle_input, output_subtitle, [])
            print(f"Cleaned subtitles saved to: {output_subtitle}")
        
        return
    
    # Step 3: Cut out segments or mute audio
    if args.mute_only:
        print("Step 3: Muting audio during profanity (keeping video intact)...")
    else:
        print("Step 3: Cutting out segments from video...")
    print("-" * 60)
    if not all_segments:
        print("  WARNING: No segments to remove! Video will be copied as-is.")
        import shutil
        shutil.copy2(input_path, output_path)
        print(f"  Video copied to: {output_path}")
    else:
        if args.mute_only:
            print(f"  Muting audio in {len(all_segments)} segment(s)...")
            total_muted_time = sum(end - start for start, end in all_segments)
            print(f"  Total time to mute: {total_muted_time:.2f} seconds ({total_muted_time/60:.2f} minutes)")
        else:
            print(f"  Removing {len(all_segments)} segment(s) from video...")
            total_removed_time = sum(end - start for start, end in all_segments)
            print(f"  Total time to remove: {total_removed_time:.2f} seconds ({total_removed_time/60:.2f} minutes)")
    cutter = VideoCutter()
    success = cutter.cut_segments(input_path, output_path, all_segments, mute_only=args.mute_only)
    print("-" * 60)
    
    if not success:
        print("Error: Failed to process video")
        sys.exit(1)
    
    # Step 4: Process subtitles (always process if available, including generated ones)
    output_subtitle = None
    if subtitle_input:
        print("Step 4: Processing subtitles...")
        
        # Determine output subtitle path
        output_base = output_path.stem
        output_dir = output_path.parent
        
        # If mute-only mode, don't adjust timestamps (video length unchanged)
        segments_for_subs = [] if args.mute_only else all_segments
        
        if subtitle_input.suffix.lower() == '.srt':
            output_subtitle = output_dir / f"{output_base}.srt"
            success = subtitle_processor.process_srt(subtitle_input, output_subtitle, segments_for_subs)
        elif subtitle_input.suffix.lower() == '.vtt':
            output_subtitle = output_dir / f"{output_base}.vtt"
            success = subtitle_processor.process_vtt(subtitle_input, output_subtitle, segments_for_subs)
        else:
            output_subtitle = output_dir / f"{output_base}{subtitle_input.suffix}"
            print(f"  Warning: Unknown subtitle format: {subtitle_input.suffix}, attempting to process as SRT...")
            success = subtitle_processor.process_srt(subtitle_input, output_subtitle, segments_for_subs)
        
        if success:
            print(f"  ✓ Cleaned subtitles saved to: {output_subtitle}")
        else:
            print(f"  ⚠ Warning: Failed to process subtitles")
        print()
    
    print("=" * 60)
    print("SUCCESS!")
    print("=" * 60)
    print(f"Cleaned video saved to: {output_path}")
    if output_subtitle:
        print(f"Cleaned subtitles saved to: {output_subtitle}")
    print(f"Removed {len(all_segments)} segment(s)")
    total_removed = sum(end - start for start, end in all_segments)
    print(f"Total time removed: {total_removed:.2f} seconds")


if __name__ == '__main__':
    main()

