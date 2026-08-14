#!/usr/bin/env python3
"""
Generate accurate subtitles for a video using Whisper
"""

import argparse
import shutil
import sys
import subprocess
import tempfile
from pathlib import Path


def seconds_to_srt_time(seconds: float) -> str:
    """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def whisper_to_srt(segments, output_path: Path):
    """Convert faster-whisper segment objects to SRT format."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments, 1):
            start_time = getattr(segment, 'start', 0)
            end_time = getattr(segment, 'end', 0)
            text = getattr(segment, 'text', '').strip()
            
            # Skip empty segments
            if not text:
                continue
            
            # Write SRT entry
            f.write(f"{i}\n")
            f.write(f"{seconds_to_srt_time(start_time)} --> {seconds_to_srt_time(end_time)}\n")
            f.write(f"{text}\n")
            f.write("\n")


def generate_subtitles(video_path: Path, output_srt: Path, model_size: str = 'base'):
    """
    Generate subtitles for a video using Whisper.
    
    Args:
        video_path: Path to input video file
        output_srt: Path to output SRT file
        model_size: Whisper model size (tiny, base, small, medium, large)
    """
    print("=" * 60)
    print("GENERATING SUBTITLES WITH WHISPER")
    print("=" * 60)
    print(f"Input video: {video_path}")
    print(f"Output SRT: {output_srt}")
    print(f"Model: {model_size}")
    print()
    
    # Check if video exists
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}")
        return False
    
    # Initialize the same faster-whisper engine used by profanity detection.
    # This avoids requiring the separate openai-whisper/PyTorch stack.
    try:
        from audio_profanity_detector_fast import AudioProfanityDetectorFast

        print(f"Loading faster-whisper model: {model_size}...")
        detector = AudioProfanityDetectorFast(
            model_size=model_size,
            auto_upgrade=False,
        )
        model = detector.whisper_model
        print(
            f"✓ faster-whisper loaded on {detector.device.upper()} "
            f"(compute_type={detector.compute_type})"
        )
    except ImportError:
        print("Error: faster-whisper not installed. Run: python3 -m pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"Error loading faster-whisper model: {e}")
        return False
    
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
        print(f"Video duration: {duration/60:.1f} minutes")
    except Exception as e:
        print(f"Warning: Could not get video duration: {e}")
        duration = None
    
    # Extract audio
    temp_dir = Path(tempfile.mkdtemp())
    audio_path = temp_dir / 'audio.wav'
    
    try:
        print(f"Extracting audio from video...")
        cmd = [
            'ffmpeg', '-i', str(video_path),
            '-ar', '16000',  # Whisper expects 16kHz
            '-ac', '1',  # Mono
            '-loglevel', 'error',
            '-y', str(audio_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"✓ Audio extracted")
    except Exception as e:
        print(f"Error extracting audio: {e}")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        return False
    
    # Transcribe with faster-whisper.
    try:
        print(
            f"Transcribing audio with faster-whisper "
            f"({detector.device.upper()}, compute_type={detector.compute_type})..."
        )
        if duration:
            print(f"⏳ Processing {duration/60:.1f} minutes of video...")
        else:
            print(f"⏳ This may take several minutes, please wait...")

        segment_generator, _info = model.transcribe(
            str(audio_path),
            word_timestamps=False,
            language='en',
            beam_size=5,
            vad_filter=True,
        )
        # Materialize before removing the temporary audio file.
        segments = list(segment_generator)

        print(f"✓ Transcription complete")
    except Exception as e:
        print(f"Error during transcription: {e}")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        return False
    
    # Convert to SRT
    try:
        print(f"Converting to SRT format...")
        whisper_to_srt(segments, output_srt)
        print(f"✓ Subtitles saved to: {output_srt}")
    except Exception as e:
        print(f"Error writing SRT file: {e}")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        return False
    
    # Clean up
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    # Show summary
    print()
    print("=" * 60)
    print("SUCCESS!")
    print("=" * 60)
    print(f"Generated {len(segments)} subtitle entries")
    print(f"Subtitles saved to: {output_srt}")
    print()
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Generate accurate subtitles for a video using Whisper'
    )
    parser.add_argument('video', type=str, help='Input video file')
    parser.add_argument('--output', '-o', type=str, default=None,
                       help='Output SRT file (default: same name as video with .srt extension)')
    parser.add_argument('--model', '-m', type=str, default='base',
                       choices=['tiny', 'base', 'small', 'medium', 'large'],
                       help='Whisper model size (default: base)')
    
    args = parser.parse_args()
    
    video_path = Path(args.video)
    
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)
    
    # Determine output path
    if args.output:
        output_srt = Path(args.output)
    else:
        output_srt = video_path.parent / f"{video_path.stem}.srt"
    
    # Create output directory if needed
    output_srt.parent.mkdir(parents=True, exist_ok=True)
    
    success = generate_subtitles(video_path, output_srt, args.model)
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()


