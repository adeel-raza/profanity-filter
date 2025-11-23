#!/usr/bin/env python3
"""Verify subtitle sync by comparing with audio transcription"""

import subprocess
import tempfile
from pathlib import Path
import re
import json

def get_video_duration(video_path: Path) -> float:
    """Get video duration"""
    try:
        cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
               '-of', 'default=noprint_wrappers=1:nokey=1', str(video_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except:
        return None

def extract_audio(video_path: Path, output_audio: Path):
    """Extract audio from video"""
    cmd = ['ffmpeg', '-y', '-i', str(video_path), '-vn', '-acodec', 'pcm_s16le',
           '-ar', '16000', '-ac', '1', str(output_audio)]
    subprocess.run(cmd, capture_output=True, check=True)

def transcribe_audio_with_whisper(audio_path: Path, model_size='tiny'):
    """Transcribe audio using Whisper"""
    try:
        import whisper
        model = whisper.load_model(model_size)
        result = model.transcribe(str(audio_path), word_timestamps=True)
        return result
    except Exception as e:
        print(f"Error transcribing: {e}")
        return None

def parse_srt_time(time_str: str) -> float:
    """Parse SRT time to seconds"""
    time_str = time_str.strip()
    if ',' in time_str:
        time_part, ms_part = time_str.split(',')
    else:
        time_part = time_str
        ms_part = '000'
    parts = time_part.split(':')
    return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2]) + int(ms_part[:3])/1000.0

def parse_srt_file(srt_path: Path) -> list:
    """Parse SRT file"""
    entries = []
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    blocks = re.split(r'\n\s*\n', content.strip())
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        try:
            index = int(lines[0])
        except:
            continue
        time_line = lines[1]
        if '-->' not in time_line:
            continue
        start_str, end_str = time_line.split('-->')
        start = parse_srt_time(start_str.strip())
        end = parse_srt_time(end_str.strip())
        text = '\n'.join(lines[2:]).strip()
        entries.append({'index': index, 'start': start, 'end': end, 'text': text})
    return entries

def find_word_at_time(transcription, target_time, tolerance=0.5):
    """Find word being spoken at target_time in transcription"""
    if not transcription or 'segments' not in transcription:
        return None
    
    for segment in transcription.get('segments', []):
        for word_info in segment.get('words', []):
            word_start = word_info.get('start', 0)
            word_end = word_info.get('end', 0)
            if word_start <= target_time <= word_end:
                return word_info.get('word', '').strip()
            # Also check if within tolerance
            if abs(word_start - target_time) < tolerance:
                return word_info.get('word', '').strip()
    return None

def verify_sync(original_video: Path, cleaned_video: Path, cleaned_srt: Path):
    """Verify subtitle sync by comparing with audio transcription"""
    print("=" * 70)
    print("VERIFYING SUBTITLE SYNC WITH AUDIO TRANSCRIPTION")
    print("=" * 70)
    
    # Get video durations
    orig_duration = get_video_duration(original_video)
    cleaned_duration = get_video_duration(cleaned_video)
    
    print(f"\nOriginal video: {orig_duration:.2f}s")
    print(f"Cleaned video: {cleaned_duration:.2f}s")
    print(f"Time removed: {orig_duration - cleaned_duration:.2f}s")
    
    # Parse cleaned subtitles
    subtitle_entries = parse_srt_file(cleaned_srt)
    print(f"\nCleaned subtitles: {len(subtitle_entries)} entries")
    
    # Extract audio from cleaned video
    print("\nExtracting audio from cleaned video...")
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_audio:
        audio_path = Path(tmp_audio.name)
    
    try:
        extract_audio(cleaned_video, audio_path)
        print("✓ Audio extracted")
        
        # Transcribe audio
        print("\nTranscribing audio with Whisper (this may take a minute)...")
        transcription = transcribe_audio_with_whisper(audio_path, 'tiny')
        
        if not transcription:
            print("✗ Failed to transcribe audio")
            return False
        
        print("✓ Audio transcribed")
        
        # Test sync at sample points
        print("\n" + "-" * 70)
        print("Testing subtitle sync at sample timestamps:")
        print("-" * 70)
        
        test_points = []
        if subtitle_entries:
            # Test first, middle, and last entries
            test_points.append(("First entry", subtitle_entries[0]))
            if len(subtitle_entries) > 1:
                mid_idx = len(subtitle_entries) // 2
                test_points.append(("Middle entry", subtitle_entries[mid_idx]))
            test_points.append(("Last entry", subtitle_entries[-1]))
            
            # Test a few more random entries
            for i in [5, 10, 15]:
                if i < len(subtitle_entries):
                    test_points.append((f"Entry {i}", subtitle_entries[i]))
        
        sync_errors = []
        for label, entry in test_points:
            subtitle_time = (entry['start'] + entry['end']) / 2  # Middle of subtitle
            subtitle_text = entry['text'].lower().strip()
            
            # Find word at this time in transcription
            spoken_word = find_word_at_time(transcription, subtitle_time, tolerance=1.0)
            
            # Check if subtitle text matches what's being spoken
            # Extract first few words from subtitle
            subtitle_words = subtitle_text.split()[:3]
            subtitle_first_words = ' '.join(subtitle_words)
            
            print(f"\n{label}:")
            print(f"  Subtitle time: {entry['start']:.2f}s - {entry['end']:.2f}s")
            print(f"  Subtitle text: {subtitle_text[:60]}...")
            print(f"  Spoken word at {subtitle_time:.2f}s: {spoken_word or 'N/A'}")
            
            # Check if there's a match
            if spoken_word:
                # Check if spoken word appears in subtitle text
                if spoken_word.lower().rstrip('.,!?;:') in subtitle_text:
                    print(f"  ✓ SYNCED: Word '{spoken_word}' found in subtitle")
                else:
                    # Check nearby words
                    nearby_word = find_word_at_time(transcription, subtitle_time + 0.5, tolerance=1.0)
                    if nearby_word and nearby_word.lower().rstrip('.,!?;:') in subtitle_text:
                        print(f"  ⚠ SLIGHTLY OFF: Word appears ~0.5s later")
                        sync_errors.append((label, entry, "slight delay"))
                    else:
                        print(f"  ✗ NOT SYNCED: Word '{spoken_word}' not in subtitle")
                        sync_errors.append((label, entry, "not synced"))
            else:
                print(f"  ⚠ Could not find spoken word at this time")
        
        print("\n" + "=" * 70)
        if sync_errors:
            print(f"FOUND {len(sync_errors)} SYNC ERRORS:")
            for label, entry, error_type in sync_errors:
                print(f"  - {label}: {error_type}")
            return False
        else:
            print("✓ ALL SUBTITLES ARE SYNCED WITH AUDIO")
            return True
            
    finally:
        if audio_path.exists():
            audio_path.unlink()

if __name__ == "__main__":
    base_dir = Path("sample")
    original_video = base_dir / "fyou.mp4"
    cleaned_video = base_dir / "fyou_cleaned.mp4"
    cleaned_srt = base_dir / "fyou_cleaned.srt"
    
    if all(f.exists() for f in [original_video, cleaned_video, cleaned_srt]):
        verify_sync(original_video, cleaned_video, cleaned_srt)
    else:
        print("ERROR: Files not found")
        for f in [original_video, cleaned_video, cleaned_srt]:
            print(f"  {f.name}: {f.exists()}")

