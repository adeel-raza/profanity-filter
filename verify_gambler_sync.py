#!/usr/bin/env python3
"""Verify The Gambler subtitle sync with audio"""

import subprocess
import tempfile
from pathlib import Path
import re

def get_video_duration(video_path: Path) -> float:
    try:
        cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
               '-of', 'default=noprint_wrappers=1:nokey=1', str(video_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except:
        return None

def extract_audio_segment(video_path: Path, start_time: float, duration: float, output_audio: Path):
    """Extract a short audio segment"""
    cmd = ['ffmpeg', '-y', '-ss', str(start_time), '-i', str(video_path),
           '-t', str(duration), '-vn', '-acodec', 'pcm_s16le', '-ar', '16000',
           '-ac', '1', str(output_audio)]
    subprocess.run(cmd, capture_output=True, check=True)

def transcribe_segment(audio_path: Path):
    """Transcribe short audio segment"""
    try:
        import whisper
        model = whisper.load_model('tiny')
        result = model.transcribe(str(audio_path), word_timestamps=True)
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

def parse_srt_time(time_str: str) -> float:
    time_str = time_str.strip()
    if ',' in time_str:
        time_part, ms_part = time_str.split(',')
    else:
        time_part = time_str
        ms_part = '000'
    parts = time_part.split(':')
    return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2]) + int(ms_part[:3])/1000.0

def parse_srt_file(srt_path: Path) -> list:
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

def verify_at_timestamp(video_path: Path, srt_path: Path, test_time: float):
    """Verify subtitle matches audio at specific timestamp"""
    print(f"\nTesting at {test_time:.2f}s:")
    
    # Find subtitle at this time
    entries = parse_srt_file(srt_path)
    matching_entry = None
    for entry in entries:
        if entry['start'] <= test_time <= entry['end']:
            matching_entry = entry
            break
    
    if not matching_entry:
        # Find closest
        closest = min(entries, key=lambda e: abs((e['start'] + e['end'])/2 - test_time))
        if abs((closest['start'] + closest['end'])/2 - test_time) < 5.0:
            matching_entry = closest
    
    if not matching_entry:
        print(f"  ✗ No subtitle found near {test_time:.2f}s")
        return False
    
    print(f"  Subtitle: {matching_entry['start']:.2f}s - {matching_entry['end']:.2f}s")
    print(f"  Text: {matching_entry['text'][:60]}...")
    
    # Extract audio segment around this time
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        audio_path = Path(tmp.name)
    
    try:
        extract_audio_segment(video_path, max(0, test_time - 1), 3.0, audio_path)
        transcription = transcribe_segment(audio_path)
        
        if transcription and 'text' in transcription:
            spoken_text = transcription['text'].strip().lower()
            subtitle_text = matching_entry['text'].lower().strip()
            
            # Check if words match
            spoken_words = set(spoken_text.split())
            subtitle_words = set(subtitle_text.split())
            
            # Find common words
            common = spoken_words & subtitle_words
            if len(common) >= 2:  # At least 2 words match
                print(f"  ✓ SYNCED: {len(common)} words match")
                print(f"    Spoken: {spoken_text[:60]}...")
                return True
            else:
                print(f"  ✗ NOT SYNCED: Only {len(common)} words match")
                print(f"    Spoken: {spoken_text[:60]}...")
                return False
        else:
            print(f"  ⚠ Could not transcribe audio")
            return False
    finally:
        if audio_path.exists():
            audio_path.unlink()

if __name__ == "__main__":
    video = Path('movies/The Gambler (2014) [1080p]/The.Gambler.2014.1080p.BluRay.x264.YIFY_cleaned.mp4')
    srt = Path('movies/The Gambler (2014) [1080p]/The.Gambler.2014.1080p.BluRay.x264.YIFY_cleaned.srt')
    
    if video.exists() and srt.exists():
        duration = get_video_duration(video)
        print(f"Video duration: {duration:.2f}s")
        
        # Test at multiple points
        test_times = [100.0, 500.0, 1000.0, 2000.0, 3000.0]
        results = []
        for t in test_times:
            if t < duration:
                result = verify_at_timestamp(video, srt, t)
                results.append(result)
        
        print(f"\n{'='*70}")
        synced = sum(results)
        total = len(results)
        print(f"Results: {synced}/{total} timestamps synced")
        if synced == total:
            print("✓ ALL SUBTITLES ARE SYNCED")
        else:
            print(f"✗ {total - synced} timestamps NOT synced")
    else:
        print("Files not found")

