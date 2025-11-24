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

from audio_profanity_detector import AudioProfanityDetector
from video_cutter import VideoCutter
from timestamp_merger import TimestampMerger
from subtitle_processor import SubtitleProcessor
from generate_subtitles import generate_subtitles


def main():
    parser = argparse.ArgumentParser(
        description='Automatically remove profanity from videos and subtitles'
    )
    parser.add_argument('input', type=str, help='Input video file (MP4, MKV, etc.)')
    parser.add_argument('output', type=str, nargs='?', default=None,
                       help='Output cleaned video file (optional - defaults to input_cleaned.ext)')
    parser.add_argument('--subs', type=str, default=None,
                       help='Input subtitle file (SRT or VTT). If not provided, will auto-detect from video name.')
    parser.add_argument('--whisper-model', type=str, default='tiny',
                       help='Whisper model size (tiny=fastest, base, small, medium, large=slowest). For long videos, use "tiny" for speed.')
    parser.add_argument('--audio', action='store_true',
                       help='Also transcribe audio for profanity detection (SLOW: 4-10 hours for 2-hour movie on CPU). Default: uses subtitles if available (FAST: minutes)')
    parser.add_argument('--remove-timestamps', type=str, default=None,
                       help='Manually specify timestamps to remove (format: "start-end,start-end" e.g., "6-11,23-30,50-60")')
    
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
    
    # Auto-detect subtitle file if not provided
    subtitle_input = None
    if args.subs:
        subtitle_input = Path(args.subs)
        if not subtitle_input.exists():
            print(f"Warning: Subtitle file not found: {subtitle_input}")
            subtitle_input = None
    else:
        # Try to find subtitle file with same name as video
        base_name = input_path.stem
        subtitle_dir = input_path.parent
        for ext in ['.srt', '.vtt']:
            potential_sub = subtitle_dir / f"{base_name}{ext}"
            if potential_sub.exists():
                subtitle_input = potential_sub
                break
    
    # If no subtitle file found, generate one first for accurate cleaning
    if not subtitle_input:
        print("=" * 60)
        print("AUTOMATED MOVIE CLEANER - PROFANITY FILTER")
        print("=" * 60)
        print(f"Input: {input_path}")
        print(f"Output: {output_path}")
        print()
        print("Step 0: Generating subtitles (required for accurate cleaning)...")
        print("-" * 60)
        print("  No subtitle file found - generating SRT from video audio...")
        print(f"  Using Whisper model: {args.whisper_model}")
        print("  ⚠ This will take 4-10 hours for a 2-hour movie on CPU")
        print("  💡 Tip: Provide subtitles with --subs for faster processing")
        print()
        
        # Generate SRT file
        subtitle_input = input_path.parent / f"{input_path.stem}.srt"
        try:
            success = generate_subtitles(input_path, subtitle_input, args.whisper_model)
            if not success:
                print("  ✗ ERROR: Failed to generate subtitles")
                print("  Continuing without subtitles (will transcribe audio on-the-fly)...")
                subtitle_input = None
            else:
                print(f"  ✓ Subtitles generated: {subtitle_input}")
                print()
        except Exception as e:
            print(f"  ✗ ERROR: Failed to generate subtitles: {e}")
            print("  Continuing without subtitles (will transcribe audio on-the-fly)...")
            subtitle_input = None
            print()
    
    print("=" * 60)
    print("AUTOMATED MOVIE CLEANER - PROFANITY FILTER")
    print("=" * 60)
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    if subtitle_input:
        print(f"Subtitles: {subtitle_input}")
    print()
    
    # Step 1: Detect profanity from subtitles (FAST) or audio (SLOW)
    # Default: Use subtitles if available (fast), only transcribe audio if no subtitles or --audio flag
    audio_segments = []
    subtitle_segments = []  # Initialize here so it's always defined
    
    # Priority 1: Use subtitles if available (FAST - completes in minutes)
    if subtitle_input:
        print("Step 1: Detecting profanity from subtitles (FAST)...")
        print("-" * 60)
        try:
            subtitle_processor = SubtitleProcessor()
            subtitle_segments = subtitle_processor.detect_profanity_segments(subtitle_input)
            print("-" * 60)
            print(f"Step 1 Summary: Found {len(subtitle_segments)} profanity segment(s) in subtitles")
            if subtitle_segments:
                for start, end, words in subtitle_segments:
                    print(f"    - {start:.2f}s to {end:.2f}s ({end-start:.2f}s): '{words}'")
            else:
                print("    No profanity detected in subtitles")
                print("    💡 Will transcribe audio to check for profanity...")
            print()
        except Exception as e:
            print(f"  ✗ ERROR: Subtitle profanity detection failed: {e}")
            print(f"  Continuing without subtitle profanity detection...")
            print()
            subtitle_segments = []  # Ensure it's set even on error
    
    # Priority 2: Transcribe audio if:
    # - --audio flag is set (user explicitly wants audio check), OR
    # - Subtitles found but no profanity detected (to catch profanity in audio)
    # Note: We no longer transcribe audio if no subtitles - we generate SRT first instead
    should_transcribe_audio = args.audio or (subtitle_input and len(subtitle_segments) == 0)
    
    if should_transcribe_audio:
        if subtitle_input and args.audio:
            print("Step 1b: Also transcribing audio (--audio flag specified)...")
            print("  ⚠ This will take 4-10 hours for a 2-hour movie on CPU")
        elif subtitle_input and len(subtitle_segments) == 0:
            print("Step 1b: No profanity in subtitles - transcribing audio to check...")
            print("  ⚠ This will take 4-10 hours for a 2-hour movie on CPU")
        
        print("-" * 60)
        try:
            audio_detector = AudioProfanityDetector(model_size=args.whisper_model)
            audio_segments = audio_detector.detect(input_path)
            print("-" * 60)
            print(f"Step 1{'b' if subtitle_input else ''} Summary: Found {len(audio_segments)} profanity segment(s) in audio")
            if audio_segments:
                for start, end, word in audio_segments:
                    print(f"    - {start:.2f}s to {end:.2f}s ({end-start:.2f}s): '{word}'")
            else:
                print("    No profanity detected in audio")
            print()
        except Exception as e:
            print(f"  ✗ ERROR: Audio profanity detection failed: {e}")
            print(f"  Continuing without audio profanity detection...")
            print()
            audio_segments = []
    elif subtitle_input:
        print("Step 1: Using subtitles only (fast mode)")
        print("  💡 To also check audio, use --audio flag (slow: 4-10 hours)")
        print()
    
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
    
    # Step 2: Merge all segments
    print("Step 2: Merging segments...")
    print(f"  Audio segments: {len(audio_segments)}")
    print(f"  Subtitle segments: {len(subtitle_segments)}")
    merger = TimestampMerger()
    all_segments = []
    if audio_segments:
        # Convert audio segments from (start, end, word) to (start, end)
        audio_segments_tuples = [(start, end) for start, end, word in audio_segments]
        all_segments = merger.merge(all_segments, audio_segments_tuples)
    if subtitle_segments:
        # Convert subtitle segments from (start, end, words) to (start, end)
        subtitle_segments_tuples = [(start, end) for start, end, words in subtitle_segments]
        all_segments = merger.merge(all_segments, subtitle_segments_tuples)
    # Add manual segments
    if manual_segments:
        print(f"  Manual segments: {len(manual_segments)}")
        all_segments = merger.merge(all_segments, manual_segments)
    print(f"  Merged into {len(all_segments)} segment(s) to remove")
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
    
    # Step 3: Cut out segments
    print("Step 3: Cutting out segments from video...")
    print("-" * 60)
    if not all_segments:
        print("  WARNING: No segments to remove! Video will be copied as-is.")
        import shutil
        shutil.copy2(input_path, output_path)
        print(f"  Video copied to: {output_path}")
    else:
        print(f"  Removing {len(all_segments)} segment(s) from video...")
        total_removed_time = sum(end - start for start, end in all_segments)
        print(f"  Total time to remove: {total_removed_time:.2f} seconds ({total_removed_time/60:.2f} minutes)")
        cutter = VideoCutter()
        success = cutter.cut_segments(input_path, output_path, all_segments)
        print("-" * 60)
        
        if not success:
            print("Error: Failed to process video")
            sys.exit(1)
    
    # Step 4: Process subtitles (always process if available, including generated ones)
    output_subtitle = None
    if subtitle_input:
        print("Step 4: Processing subtitles...")
        subtitle_processor = SubtitleProcessor()
        
        # Determine output subtitle path
        output_base = output_path.stem
        output_dir = output_path.parent
        
        if subtitle_input.suffix.lower() == '.srt':
            output_subtitle = output_dir / f"{output_base}.srt"
            success = subtitle_processor.process_srt(subtitle_input, output_subtitle, all_segments)
        elif subtitle_input.suffix.lower() == '.vtt':
            output_subtitle = output_dir / f"{output_base}.vtt"
            success = subtitle_processor.process_vtt(subtitle_input, output_subtitle, all_segments)
        else:
            output_subtitle = output_dir / f"{output_base}{subtitle_input.suffix}"
            print(f"  Warning: Unknown subtitle format: {subtitle_input.suffix}, attempting to process as SRT...")
            success = subtitle_processor.process_srt(subtitle_input, output_subtitle, all_segments)
        
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

