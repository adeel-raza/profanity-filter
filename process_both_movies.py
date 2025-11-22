#!/usr/bin/env python3
"""
Process both movies (Code_3 and argo) and generate summary
"""

import subprocess
import sys
from pathlib import Path
import time


def process_movie(input_video, output_video, subtitle_file, movie_name):
    """Process a single movie"""
    print("=" * 70)
    print(f"Processing: {movie_name}")
    print("=" * 70)
    print(f"Input:  {input_video}")
    print(f"Output: {output_video}")
    print(f"Subs:   {subtitle_file}")
    print()
    
    script_dir = Path(__file__).parent
    cmd = [
        sys.executable,
        str(script_dir / 'clean.py'),
        str(input_video),
        str(output_video),
        '--subs', str(subtitle_file)
    ]
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, check=True)
        elapsed = time.time() - start_time
        print(f"\n✓ {movie_name} processed successfully in {elapsed/60:.1f} minutes")
        return True
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"\n✗ {movie_name} failed after {elapsed/60:.1f} minutes")
        return False


def main():
    base_dir = Path("/home/adeel/Link to html/wp_local/movie_cleaner")
    output_dir = base_dir / "movies" / "cleaned"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    movies = [
        {
            'name': 'Code_3',
            'input': base_dir / "movies" / "Code_3.mkv",
            'output': output_dir / "Code_3_cleaned.mkv",
            'subs': base_dir / "movies" / "Code_3.srt"
        },
        {
            'name': 'argo',
            'input': base_dir / "movies" / "argo" / "argo.mp4",
            'output': output_dir / "argo_cleaned.mp4",
            'subs': base_dir / "movies" / "argo" / "argo.srt"
        }
    ]
    
    print("=" * 70)
    print("MOVIE CLEANING - BATCH PROCESS")
    print("=" * 70)
    print(f"Movies to process: {len(movies)}")
    print()
    
    results = []
    for movie in movies:
        if not movie['input'].exists():
            print(f"⚠ Skipping {movie['name']}: Input file not found")
            continue
        
        if not movie['subs'].exists():
            print(f"⚠ Warning: Subtitle file not found for {movie['name']}")
        
        success = process_movie(
            movie['input'],
            movie['output'],
            movie['subs'],
            movie['name']
        )
        results.append((movie['name'], success))
        print()
    
    # Generate summary
    print("=" * 70)
    print("GENERATING SUMMARY")
    print("=" * 70)
    print()
    
    summary_cmd = [
        sys.executable,
        str(base_dir / 'generate_summary.py'),
        str(base_dir / "movies"),
        str(output_dir)
    ]
    
    try:
        subprocess.run(summary_cmd, check=True)
    except Exception as e:
        print(f"Error generating summary: {e}")
    
    # Final status
    print()
    print("=" * 70)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 70)
    for name, success in results:
        status = "✓ Success" if success else "✗ Failed"
        print(f"  {name}: {status}")
    print()


if __name__ == '__main__':
    main()




