#!/usr/bin/env python3
"""
Batch process videos from input directory to output directory
"""

import sys
import subprocess
from pathlib import Path
import argparse


def batch_process(input_dir: Path, output_dir: Path, **kwargs):
    """
    Process all videos in input directory and save to output directory.
    
    Args:
        input_dir: Directory containing input videos
        output_dir: Directory to save filtered videos
        **kwargs: Additional arguments for clean.py (whisper_model, etc.)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all video files
    video_extensions = ['.mp4', '.mkv', '.mov', '.avi', '.flv', '.webm']
    video_files = []
    for ext in video_extensions:
        video_files.extend(input_dir.rglob(f'*{ext}'))
    
    if not video_files:
        print(f"No video files found in {input_dir}")
        return
    
    print(f"Found {len(video_files)} video file(s) to process")
    print("=" * 60)
    
    processed = 0
    failed = 0
    
    # Get the directory of this script
    script_dir = Path(__file__).parent
    
    for i, video_path in enumerate(video_files, 1):
        print(f"\n[{i}/{len(video_files)}] Processing: {video_path.name}")
        print("-" * 60)
        
        # Generate output filename
        output_name = f"{video_path.stem}_cleaned{video_path.suffix}"
        output_path = output_dir / output_name
        
        # Check for subtitle file
        subtitle_path = None
        for sub_ext in ['.srt', '.vtt']:
            potential_sub = video_path.parent / f"{video_path.stem}{sub_ext}"
            if potential_sub.exists():
                subtitle_path = potential_sub
                break
            # Also check for .en.srt pattern
            potential_sub_en = video_path.parent / f"{video_path.stem}.en{sub_ext}"
            if potential_sub_en.exists():
                subtitle_path = potential_sub_en
                break
        
        # Build command
        cmd = [
            sys.executable,
            str(script_dir / 'clean.py'),
            str(video_path),
            str(output_path)
        ]
        
        if subtitle_path:
            cmd.extend(['--subs', str(subtitle_path)])
        
        # Add optional arguments
        if kwargs.get('whisper_model'):
            cmd.extend(['--whisper-model', kwargs['whisper_model']])
        if kwargs.get('no_audio'):
            cmd.append('--no-audio')
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=False)
            processed += 1
            print(f"✓ Successfully processed: {output_path.name}")
        except subprocess.CalledProcessError as e:
            failed += 1
            print(f"✗ Failed to process {video_path.name}")
        except Exception as e:
            failed += 1
            print(f"✗ Error processing {video_path.name}: {e}")
    
    print("\n" + "=" * 60)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Successfully processed: {processed}")
    print(f"Failed: {failed}")
    print(f"Total: {len(video_files)}")
    print(f"\nFiltered videos saved to: {output_dir}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Batch process videos from input directory to output directory'
    )
    parser.add_argument('input_dir', type=str, help='Input directory containing videos')
    parser.add_argument('output_dir', type=str, help='Output directory for filtered videos')
    parser.add_argument('--whisper-model', type=str, default='tiny',
                       help='Whisper model size (tiny, base, small, medium, large)')
    parser.add_argument('--no-audio', action='store_true',
                       help='Skip audio profanity detection')
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        sys.exit(1)
    
    batch_process(
        input_dir,
        output_dir,
        whisper_model=args.whisper_model,
        no_audio=args.no_audio
    )

