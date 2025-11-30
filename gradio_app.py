"""
Gradio Web Interface for Movie Profanity Filter
Deploy to Hugging Face Spaces for free hosting
"""

import gradio as gr
import tempfile
import os
from pathlib import Path
import sys
from io import StringIO
import shutil

# Import cleaning components
from audio_profanity_detector import AudioProfanityDetector
from video_cutter import VideoCutter
from timestamp_merger import TimestampMerger
from subtitle_processor import SubtitleProcessor


def clean_video(video_file, subtitle_file, progress=gr.Progress()):
    """
    Clean video using the profanity filter
    
    Args:
        video_file: Uploaded video file (Gradio file object)
        subtitle_file: Optional subtitle file (Gradio file object)
        whisper_model: Whisper model size
        progress: Gradio progress tracker
        
    Returns:
        Tuple of (cleaned_video_path, cleaned_subtitle_path, log_output)
    """
    if video_file is None:
        return None, None, "Error: Please upload a video file"
    
    log_messages = []
    
    try:
        # Create temporary directory for processing
        temp_dir = Path(tempfile.mkdtemp())
        input_video = Path(video_file.name)
        output_video = temp_dir / f"cleaned_{input_video.name}"
        
        log_messages.append(f"Input: {input_video.name}")
        log_messages.append(f"Output: {output_video.name}")
        
        # Handle subtitle file
        subtitle_path = None
        if subtitle_file is not None:
            subtitle_path = Path(subtitle_file.name)
            log_messages.append(f"Subtitles: {subtitle_path.name}")
        
        # Step 1: Detect profanity in audio
        audio_segments = []
        progress(0.1, desc="Loading Whisper model...")
        log_messages.append("\nStep 1: Detecting profanity in audio...")
        
        try:
            # Use 'tiny' model by default for fast processing
            audio_detector = AudioProfanityDetector(model_size='tiny')
            progress(0.2, desc="Transcribing audio with Whisper...")
            audio_segments = audio_detector.detect(input_video)
            
            log_messages.append(f"Found {len(audio_segments)} profanity segment(s)")
            if audio_segments:
                for start, end, word in audio_segments[:3]:  # Show first 3
                    log_messages.append(f"  {start:.1f}s-{end:.1f}s: '{word}'")
                if len(audio_segments) > 3:
                    log_messages.append(f"  ... {len(audio_segments) - 3} more")
        except Exception as e:
            log_messages.append(f"ERROR: Audio profanity detection failed: {e}")
            audio_segments = []
        
        # Step 2: Merge segments
        progress(0.4, desc="Merging segments...")
        log_messages.append("\nStep 2: Merging segments...")
        merger = TimestampMerger()
        all_segments = []
        if audio_segments:
            audio_segments_tuples = [(start, end) for start, end, word in audio_segments]
            all_segments = merger.merge(all_segments, audio_segments_tuples)
            log_messages.append(f"Merged into {len(all_segments)} segment(s) to remove")
        
        if not all_segments:
            progress(0.6, desc="No profanity detected. Processing subtitles...")
            log_messages.append("\nNo profanity detected. Copying video as-is...")
            # Copy video as-is
            shutil.copy2(input_video, output_video)
            
            # Process subtitles if provided
            cleaned_subtitle = None
            if subtitle_path and subtitle_path.exists():
                subtitle_processor = SubtitleProcessor()
                output_base = output_video.stem
                output_dir = output_video.parent
                
                if subtitle_path.suffix.lower() == '.srt':
                    output_subtitle = output_dir / f"{output_base}.srt"
                    subtitle_processor.process_srt(subtitle_path, output_subtitle, [])
                    cleaned_subtitle = str(output_subtitle)
                elif subtitle_path.suffix.lower() == '.vtt':
                    output_subtitle = output_dir / f"{output_base}.vtt"
                    subtitle_processor.process_vtt(subtitle_path, output_subtitle, [])
                    cleaned_subtitle = str(output_subtitle)
            
            progress(1.0, desc="Complete!")
            log_messages.append("\n✓ No profanity found - video copied")
            return str(output_video), cleaned_subtitle, "\n".join(log_messages)
        
        # Step 3: Cut out segments
        progress(0.6, desc="Cutting out profanity segments...")
        log_messages.append(f"\nStep 3: Cutting {len(all_segments)} segment(s)...")
        total_removed = sum(end - start for start, end in all_segments)
        log_messages.append(f"Removing {total_removed:.1f}s...")
        
        cutter = VideoCutter()
        success = cutter.cut_segments(input_video, output_video, all_segments)
        
        if not success:
            raise Exception("Failed to process video")
        
        log_messages.append("✓ Complete")
        
        # Step 4: Process subtitles
        cleaned_subtitle = None
        if subtitle_path and subtitle_path.exists():
            progress(0.8, desc="Processing subtitles...")
            log_messages.append("\nStep 4: Processing subtitles...")
            subtitle_processor = SubtitleProcessor()
            output_base = output_video.stem
            output_dir = output_video.parent
            
            if subtitle_path.suffix.lower() == '.srt':
                output_subtitle = output_dir / f"{output_base}.srt"
                subtitle_processor.process_srt(subtitle_path, output_subtitle, all_segments)
                cleaned_subtitle = str(output_subtitle)
            elif subtitle_path.suffix.lower() == '.vtt':
                output_subtitle = output_dir / f"{output_base}.vtt"
                subtitle_processor.process_vtt(subtitle_path, output_subtitle, all_segments)
                cleaned_subtitle = str(output_subtitle)
            
            log_messages.append("✓ Subtitles cleaned")
        
        progress(1.0, desc="Complete!")
        log_messages.append("\n✓ SUCCESS")
        log_messages.append(f"Video: {output_video.name}")
        if cleaned_subtitle:
            log_messages.append(f"Subtitles: {Path(cleaned_subtitle).name}")
        log_messages.append(f"Removed: {len(all_segments)} segment(s), {total_removed:.1f}s")
        
        return str(output_video), cleaned_subtitle, "\n".join(log_messages)
        
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        log_messages.append(f"\n{error_msg}")
        return None, None, "\n".join(log_messages)


# Create Gradio interface
def create_interface():
    """Create and return Gradio interface"""
    
    # Use compatible Gradio version - theme parameter not available in older versions
    # Remove theme parameter for compatibility with Hugging Face Spaces
    with gr.Blocks(title="Free Profanity Filter for Movies & Videos - VidAngel & ClearPlay Alternative") as demo:
        gr.Markdown("""
# Free Profanity Filter for Movies & Videos - VidAngel & ClearPlay Alternative

**Created by [Adeel Raza](https://elearningevolve.com/about) - Contact: info@elearningevolve.com**

**Watch movies YOUR way - completely FREE!** Remove profanity, curse words, and offensive language from ANY video automatically. No subscription or Netflix account required. Works with local video files, YouTube downloads, and any MP4/MKV content.

**Perfect for families who want to enjoy movies together without inappropriate language**  
**100% FREE alternative to VidAngel ($9.99/month) and ClearPlay ($7.99/month)**  
**Privacy-focused: Everything runs locally on your computer**  
**AI-powered with enhanced dialogue detection using faster-whisper**

---

## Why Choose This Free Profanity Filter?

### Save Money - No Subscriptions
- **VidAngel**: $9.99/month + requires Netflix/Amazon Prime  
- **ClearPlay**: $7.99/month + requires compatible devices  
- **This App**: **100% FREE** - works with any video file

### Watch Movies Your Way
Unlike VidAngel and ClearPlay that only work with specific streaming services, this tool works with:  
- Local video files (MP4, MKV, AVI, etc.)  
- YouTube downloads (via yt-dlp)  
- DVDs and Blu-rays (ripped to digital)  
- ANY video source - no restrictions

### Privacy & Control
- Everything runs on **YOUR computer**  
- **No cloud uploads** or streaming required  
- Your videos stay private  
- Complete control over content filtering

---

## How It Works

- AI Audio Transcription (Word-Level Precision): Uses the base model by default for best accuracy. Each word gets a precise timestamp (+/-0.1s). Only the bad words are cut, not whole sentences.
- Smart Multi-Word Detection: Detects 1,192+ profanity words and intelligently merges phrases like "fuck you" or "bull shit". Whole-word matching prevents false positives.
- Frame-Accurate Video Cutting: FFmpeg-powered, removes only profanity segments (0.3-2s each), preserves original quality, and ensures smooth transitions.

---

## Usage

**Basic:**
```bash
python3 clean.py input.mp4 output.mp4
# Output: output.mp4 (cleaned)
```

**Faster (less accurate):**
```bash
python3 clean.py input.mp4 output.mp4 --model tiny
# Tiny model is faster but may miss profanity, especially in movies with music or background noise.
```

**Subtitles:**
- If your subtitle file has the same name as your video (e.g. `movie.mp4` and `movie.srt`) and is in the same directory, it will be auto-detected. You do not need to specify `--subs` in this case.

**Manual:**
```bash
python3 clean.py input.mp4 output.mp4 --subs custom_subs.srt
```

---

## System Requirements
- 2-hour movie takes ~6 hours on CPU (base model)
- GPU (optional): 30-60 minutes
- RAM: 8GB or more recommended

---

**Open Source. No subscription. No cloud uploads. Your movies, your way.**
        """)
        
        # Upload section at top
        with gr.Row():
            with gr.Column():
                video_input = gr.File(
                    label="Upload Video",
                    file_types=["video"],
                    type="filepath"
                )
                
                subtitle_input = gr.File(
                    label="Upload Subtitles (Optional - SRT or VTT)",
                    file_types=[".srt", ".vtt"],
                    type="filepath"
                )
                
                process_btn = gr.Button("Clean Video", variant="primary", size="lg")
        
        gr.Markdown("""
### How It Works
Upload your video -> AI transcribes audio -> Detects profanity -> Removes offensive segments -> Download clean version!

**Perfect for**: Family movie nights, Religious communities, Elderly care, Educational settings, Content creators, Anyone who prefers clean content
        """)
        
        # Output section
        with gr.Row():
            with gr.Column():
                video_output = gr.File(
                    label="Cleaned Video",
                    type="filepath"
                )
                
                subtitle_output = gr.File(
                    label="Cleaned Subtitles",
                    type="filepath"
                )
                
                log_output = gr.Textbox(
                    label="Processing Log",
                    lines=15,
                    max_lines=20,
                    interactive=False
                )
        
        gr.Markdown("""
# Free Profanity Filter for Movies & Videos - VidAngel & ClearPlay Alternative

**Created by [Adeel Raza](https://elearningevolve.com/about) - Contact: info@elearningevolve.com**

### Processing Time & System Requirements

**With AI Transcription (Recommended):**
- Short videos (5-15 min): 2-5 minutes processing
- Full movies (90-120 min): 15-30 minutes processing
- Long content (2-3 hours): 30-45 minutes processing

**With Subtitles (Faster):**
- Any length: ~10-20 minutes for cutting/encoding

**Formats:** MP4, MKV, MOV, AVI | **Privacy:** Files auto-deleted after processing | **Limit:** 5GB

### Free to Install on Your PC
Want faster processing? Download and run on your own computer - completely FREE!
- No internet required after setup
- Process unlimited videos locally
- Better performance on your hardware
- [Download from GitHub](https://github.com/adeel-raza/profanity-filter)
        """)
        
        # Connect the interface
        process_btn.click(
            fn=clean_video,
            inputs=[video_input, subtitle_input],
            outputs=[video_output, subtitle_output, log_output]
        )
        
        gr.Markdown("""
        ### How to Use (Simple 3-Step Process)
        
        1. **Upload** your video file (MP4, MKV, etc.)
        2. **Optional**: Upload subtitle file for faster processing (SRT/VTT)
        3. **Click** "Clean Video" and wait for processing to complete
        4. **Download** your family-friendly clean video!
        
        The AI automatically transcribes audio, detects 1,132+ profanity words, removes offensive segments, and generates clean subtitles.
        
        ### Compare to Paid Services
        
        | Feature | This Tool | VidAngel | ClearPlay |
        |---------|-----------|----------|-----------|
        | **Cost** | **FREE** | $9.99/mo | $7.99/mo |
        | **Video Source** | **Any file** | Netflix/Prime only | Limited services |
        | **Internet** | **Optional** | Required | Required |
        | **Privacy** | **100% secure** | Account required | Account required |
        | **Download** | **✅ Yes** | ❌ Streaming only | ❌ Streaming only |
        
        ### Perfect For
        - **Parents**: Create G/PG versions of PG-13/R movies for kids
        - **Religious Groups**: Clean content for church events and gatherings
        - **Educators**: Use movie clips in classrooms appropriately
        - **Elderly Care**: Provide entertainment without modern profanity
        - **Content Creators**: Clean source material for family YouTube channels
        - **Personal Preference**: Enjoy movies without constant cursing!
        
        ### Privacy & Security
        Your videos are processed securely on this server and automatically deleted after download. No data is stored or shared. For complete privacy, download the tool and run locally on your computer!
        
        ### Keywords
        Profanity filter, Netflix profanity filter, Movie content filter, VidAngel alternative, ClearPlay alternative, Family-friendly movies, Remove curse words, Clean movie versions, Enjoy movies your way, Free video filter, Parental controls
        
        ---
        
        **Save $96-120 per year** compared to VidAngel or ClearPlay subscriptions. Enjoy unlimited family-friendly content filtering!
        """)
    
    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)

