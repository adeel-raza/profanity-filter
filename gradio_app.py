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
    with gr.Blocks(title="Movie Profanity Filter") as demo:
        gr.Markdown("""
        # Movie Profanity Filter
        
        Remove profanity from videos using AI. Upload video and optional subtitles to create family-friendly content.
        
        **Features:** OpenAI Whisper transcription • 1,132+ profanity words detected • Automatic video cutting • Subtitle cleaning
        """)
        
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
        **Processing:** ~10-30 min for 2-hour movie with subtitles (recommended). Without subtitles: 4-10 hours.  
        **Formats:** MP4, MKV, MOV, AVI. **Privacy:** Files deleted after processing. **Limit:** 5 GB (platform limit).
        """)
        
        # Connect the interface
        process_btn.click(
            fn=clean_video,
            inputs=[video_input, subtitle_input],
            outputs=[video_output, subtitle_output, log_output]
        )
        
        gr.Markdown("""
        **How it works:** Upload video → (Optional) Add subtitles → Click "Clean Video" → Download cleaned files.  
        The tool transcribes audio, detects profanity, cuts segments, and cleans subtitles automatically.
        """)
    
    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)

