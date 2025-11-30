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
    import time
    overall_start_time = time.time()
    parser = argparse.ArgumentParser(
        description='Automatically remove profanity from videos using AI transcription'
    )
    parser.add_argument('input', type=str, help='Input video file (MP4, MKV, etc.)')
    parser.add_argument('output', type=str, nargs='?', default=None,
                       help='Output cleaned video file (optional - defaults to input_cleaned.ext)')
    parser.add_argument('--subs', type=str, default=None,
                       help='Use existing subtitle file instead of transcribing audio (SRT or VTT format). By default, the tool auto-detects a matching subtitle next to the video (same basename). Only use this flag if the subs are in a different location/name.')
    parser.add_argument('--srt-window', type=float, default=None,
                       help='[Advanced] When using subtitle-driven detection (see --use-subs-detection), removal uses the full cue by default. Set a positive window (seconds) to limit removal around cue center.')
    parser.add_argument('--pad', type=float, default=0.0,
                       help='[Advanced] Extra padding (seconds) added before/after each subtitle cue when removing in subtitle-driven detection. Default: 0.0')
    parser.add_argument('--merge-gap', type=float, default=0.06,
                       help='Max gap (seconds) between segments to merge. Default: 0.06 (minimal, per-word behavior)')
    parser.add_argument('--expand-pad', type=float, default=0.15,
                       help='Expand each detected segment by this padding before cutting (applied to start and end). Default: 0.15 (150ms) to ensure complete removal')
    parser.add_argument('--model', type=str, default='base',
                       help='Whisper model size: tiny (fastest), base (recommended), small, medium, large (most accurate). Default: base')
    parser.add_argument('--force-audio', action='store_true',
                       help='Use audio transcription to detect profanities (default behavior). Subtitles, if provided/auto-detected, are used only for text cleaning and embedding.')
    parser.add_argument('--use-subs-detection', action='store_true',
                       help='[Advanced] Use provided/auto-detected subtitles for profanity detection instead of audio. Not recommended unless you specifically want cue-level removal.')
    parser.add_argument('--phrase-gap', type=float, default=2.0,
                       help='Max gap (seconds) between consecutive detected profanity words to merge into one phrase segment. Default: 2.0')
    parser.add_argument('--remove-timestamps', type=str, default=None,
                       help='Manually specify additional timestamps to remove (format: "start-end,start-end" e.g., "6-11,23-30")')
    parser.add_argument('--log-time', type=str, default=None,
                       help='Optional: path to write total cutting time (seconds).')
    parser.add_argument('--dump-transcript', type=str, default=None,
                       help='Write raw transcript words with start/end timestamps to this file.')
    parser.add_argument('--dialog-enhance', action='store_true', default=True,
                       help='Apply speech-focused audio filtering (HPF/LPF + normalization) before transcription to improve recognition. Enabled by default.')
    parser.add_argument('--no-dialog-enhance', action='store_false', dest='dialog_enhance',
                       help='Disable dialog enhancement.')
    parser.add_argument('--min-wpm', type=float, default=50.0,
                       help='Warn if transcript words per minute fall below this value. Default: 50.0')
    parser.add_argument('--auto-upgrade-model', action='store_true', default=True,
                       help='Automatically retry transcription with the next larger model once if WPM < --min-wpm. Enabled by default.')
    parser.add_argument('--no-auto-upgrade', action='store_false', dest='auto_upgrade_model',
                       help='Disable automatic model upgrade.')
    
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
    
    # Determine subtitle source: prefer auto-detected subs with same basename; else use --subs; else none
    subtitle_input = None
    if args.subs:
        # Explicit subtitle path provided
        candidate = Path(args.subs)
        if candidate.exists():
            subtitle_input = candidate
        else:
            print(f"Warning: Subtitle file not found: {candidate}")
            print(f"Falling back to auto-detect and/or audio transcription...")
    else:
        # Auto-detect subtitles with same basename in the input directory
        srt_candidate = input_path.with_suffix('.srt')
        vtt_candidate = input_path.with_suffix('.vtt')
        if srt_candidate.exists():
            subtitle_input = srt_candidate
        elif vtt_candidate.exists():
            subtitle_input = vtt_candidate
    
    print("=" * 60)
    print("AUTOMATED MOVIE CLEANER - PROFANITY FILTER")
    print("=" * 60)
    subtitle_processor = SubtitleProcessor() if subtitle_input else None
    
    # Step 1: Detect profanity using AI transcription (faster-whisper)
    # Uses word-level timestamps for precise, accurate profanity removal
    audio_segments = []
    
    # Default: audio-only detection for precise per-word cuts
    use_subs_for_detection = bool(subtitle_input) and args.use_subs_detection and not args.force_audio
    if use_subs_for_detection:
        print("Step 1: Using provided subtitle file for profanity detection")
        print("-" * 60)
        print("Step 1a: Detecting profanity from subtitles...")
        if subtitle_processor:
            subtitle_segments = subtitle_processor.detect_profanity_segments(subtitle_input, srt_window=args.srt_window, pad=args.pad)
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
            audio_detector = AudioProfanityDetectorFast(
                model_size=args.model,
                phrase_gap=args.phrase_gap,
                dialog_enhance=args.dialog_enhance,
                dump_transcript_path=args.dump_transcript,
                min_wpm=args.min_wpm,
                auto_upgrade=args.auto_upgrade_model,
            )
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
    merger = TimestampMerger(merge_gap=args.merge_gap)
    all_segments = []
    
    # Use audio segments (word-level timestamps from Whisper)
    # This matches the Gradio app which uses ONLY audio transcription
    if audio_segments:
        # Convert audio segments from (start, end, word) to (start, end)
        audio_segments_tuples = [(start, end) for start, end, word in audio_segments]
        all_segments = merger.merge([], audio_segments_tuples)
        print(f"  Merged into {len(all_segments)} segment(s) to remove")
    
    # Add manual segments if specified
    if manual_segments:
        print(f"  Manual segments: {len(manual_segments)}")
        all_segments = merger.merge(all_segments, manual_segments)
        print(f"  Total after manual: {len(all_segments)} segment(s) to remove")
    if all_segments:
        for i, (start, end) in enumerate(all_segments, 1):
            print(f"    {i}. {start:.2f}s to {end:.2f}s ({end-start:.2f}s)")
    else:
        print("    WARNING: No segments to remove!")
    print()

    # Safety expansion: dilate segments slightly to catch partial profanities
    if all_segments:
        print("Step 2b: Expanding segments to catch clipped syllables...")
        expanded = []
        for (start, end) in all_segments:
            new_start = max(0.0, start - args.expand_pad)
            new_end = end + args.expand_pad
            expanded.append((new_start, new_end))
        # Re-merge after expansion to combine overlaps
        all_segments = TimestampMerger(merge_gap=args.merge_gap).merge([], expanded)
        for i, (start, end) in enumerate(all_segments, 1):
            print(f"    {i}. {start:.2f}s to {end:.2f}s ({end-start:.2f}s)")
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
    cutting_start = time.time()
    success = cutter.cut_segments(input_path, output_path, all_segments)
    elapsed = time.time() - cutting_start
    print("-" * 60)
    print(f"Total video cutting time: {elapsed:.2f} seconds")
    # Always log cutting time next to output video as a sidecar file
    try:
        sidecar_time = output_path.with_suffix('.time.txt')
        with open(sidecar_time, 'w') as f:
            f.write(f"cutting_seconds={elapsed:.3f}\n")
        print(f"Cutting time written to: {sidecar_time}")
    except Exception as e:
        print(f"Warning: failed to write cutting-time file: {e}")
    
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
        
        # Adjust subtitles based on removed segments
        segments_for_subs = all_segments
        
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
    else:
        # No subtitle provided: generate subtitles for the cleaned video and attach
        try:
            print("Step 4: Generating subtitles for cleaned video...")
            output_dir = output_path.parent
            output_base = output_path.stem
            output_subtitle = output_dir / f"{output_base}.srt"
            ok = generate_subtitles(output_path, output_subtitle, args.model)
            if ok:
                print(f"  ✓ Subtitles generated and saved to: {output_subtitle}")
            else:
                print("  ⚠ Warning: Failed to generate subtitles for cleaned video")
        except Exception as e:
            print(f"  ⚠ Warning: Subtitle generation error: {e}")
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
    # Overall runtime (end-to-end)
    overall_elapsed = time.time() - overall_start_time
    print(f"Total end-to-end processing time: {overall_elapsed:.2f} seconds")
    # Always log overall time next to output
    try:
        sidecar_total = output_path.with_suffix('.total_time.txt')
        with open(sidecar_total, 'w') as f:
            f.write(f"total_seconds={overall_elapsed:.3f}\n")
        print(f"Overall processing time written to: {sidecar_total}")
    except Exception as e:
        print(f"Warning: failed to write total-time file: {e}")

    # Optional: mux subtitles into the cleaned video container so players auto-load them
    try:
        if output_subtitle and output_path.suffix.lower() in {'.mp4', '.mkv'}:
            print("\nAttaching subtitles track to the cleaned video for auto-display...")
            import subprocess
            temp_muxed = output_path.with_name(f"{output_path.stem}_with_subs{output_path.suffix}")
            # For MP4, convert SRT to mov_text; for MKV, we can copy srt
            if output_path.suffix.lower() == '.mp4':
                cmd = [
                    'ffmpeg', '-i', str(output_path), '-i', str(output_subtitle),
                    '-map', '0', '-map', '1', '-c:v', 'copy', '-c:a', 'copy', '-c:s', 'mov_text',
                    '-metadata:s:s:0', 'language=en', '-loglevel', 'error', '-y', str(temp_muxed)
                ]
            else:  # .mkv
                cmd = [
                    'ffmpeg', '-i', str(output_path), '-i', str(output_subtitle),
                    '-map', '0', '-map', '1', '-c', 'copy',
                    '-metadata:s:s:0', 'language=en', '-loglevel', 'error', '-y', str(temp_muxed)
                ]
            subprocess.run(cmd, check=True)
            # Replace original with muxed to keep expected filename
            import os
            os.replace(temp_muxed, output_path)
            print(f"✓ Subtitles attached inside: {output_path}")
    except Exception as e:
        print(f"⚠ Warning: Failed to attach subtitles into video: {e}")


if __name__ == '__main__':
    main()

