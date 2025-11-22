#!/usr/bin/env python3
"""
Generate detailed summary showing what segments were removed
"""

import sys
from pathlib import Path
from subtitle_processor import SubtitleProcessor


def format_time(seconds: float) -> str:
    """Format seconds as MM:SS"""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def analyze_subtitle_changes(original_srt: Path, cleaned_srt: Path) -> dict:
    """Compare original and cleaned subtitles to see what was removed"""
    if not original_srt.exists() or not cleaned_srt.exists():
        return None
    
    processor = SubtitleProcessor()
    
    # Parse both files
    with open(original_srt, 'r', encoding='utf-8') as f:
        original_content = f.read()
    original_entries = processor._parse_srt(original_content)
    
    with open(cleaned_srt, 'r', encoding='utf-8') as f:
        cleaned_content = f.read()
    cleaned_entries = processor._parse_srt(cleaned_content)
    
    # Find removed entries (in original but not in cleaned after accounting for time shifts)
    removed_entries = []
    cleaned_times = {(e['start'], e['end']) for e in cleaned_entries}
    
    for orig_entry in original_entries:
        # Check if this entry exists in cleaned (accounting for time adjustment)
        found = False
        for cleaned_entry in cleaned_entries:
            # Check if text matches (simpler than time matching due to adjustments)
            if orig_entry['text'].strip() == cleaned_entry['text'].strip():
                found = True
                break
        
        if not found:
            removed_entries.append(orig_entry)
    
    return {
        'original_count': len(original_entries),
        'cleaned_count': len(cleaned_entries),
        'removed_count': len(removed_entries),
        'removed_entries': removed_entries[:10]  # First 10 removed entries
    }


def generate_detailed_summary(input_dir: Path, output_dir: Path):
    """Generate detailed summary report"""
    print("=" * 70)
    print("DETAILED CLEANING SUMMARY")
    print("=" * 70)
    print()
    
    # Find all cleaned videos
    cleaned_videos = list(output_dir.glob('*_cleaned.mp4'))
    
    if not cleaned_videos:
        print(f"No cleaned videos found in {output_dir}")
        return
    
    print(f"Found {len(cleaned_videos)} cleaned video(s)\n")
    
    for i, cleaned_video in enumerate(cleaned_videos, 1):
        video_name = cleaned_video.stem.replace('_cleaned', '')
        print(f"[{i}] {video_name}")
        print("-" * 70)
        
        # Find original video
        original_video = None
        for ext in ['.mp4', '.mkv', '.mov', '.avi']:
            potential = input_dir / f"{video_name}{ext}"
            if potential.exists():
                original_video = potential
                break
        
        if not original_video:
            print(f"  ⚠ Original video not found")
            continue
        
        # Check for subtitle files
        cleaned_srt = output_dir / f"{cleaned_video.stem}.srt"
        original_srt = None
        
        # Try to find original subtitle
        for sub_file in input_dir.glob(f"{video_name}*.srt"):
            original_srt = sub_file
            break
        
        if original_srt and cleaned_srt.exists():
            subtitle_analysis = analyze_subtitle_changes(original_srt, cleaned_srt)
            if subtitle_analysis:
                print(f"  Subtitles:")
                print(f"    Original entries: {subtitle_analysis['original_count']}")
                print(f"    Cleaned entries:  {subtitle_analysis['cleaned_count']}")
                print(f"    Removed entries:  {subtitle_analysis['removed_count']}")
                
                if subtitle_analysis['removed_entries']:
                    print(f"    Sample removed subtitles:")
                    for entry in subtitle_analysis['removed_entries'][:3]:
                        print(f"      {format_time(entry['start'])}-{format_time(entry['end'])}: {entry['text'][:50]}...")
        else:
            print(f"  Subtitles: Not available")
        
        print()
    
    print("=" * 70)
    print("Note: For detailed segment information, check the processing logs")
    print("or use: python quick_preview.py <video.mp4> to see what will be removed")
    print("=" * 70)


def main():
    if len(sys.argv) < 3:
        print("Usage: python detailed_summary.py <input_dir> <output_dir>")
        sys.exit(1)
    
    input_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    
    generate_detailed_summary(input_dir, output_dir)


if __name__ == '__main__':
    main()




