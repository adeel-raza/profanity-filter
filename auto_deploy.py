#!/usr/bin/env python3
"""
Automated deployment script for Hugging Face Spaces
This will create the Space and upload all necessary files
"""

import os
import sys
from pathlib import Path
from huggingface_hub import HfApi, create_repo, upload_file
import subprocess

def main():
    print("=" * 60)
    print("Movie Profanity Filter - Auto Deploy to HF Spaces")
    print("=" * 60)
    print()
    
    # Check if logged in
    api = HfApi()
    try:
        user = api.whoami()
        username = user['name']
        print(f"✓ Logged in as: {username}")
    except Exception as e:
        print("✗ Not logged in to Hugging Face")
        print()
        print("Please login first:")
        print("  huggingface-cli login")
        print()
        print("Or run:")
        print("  python3 -c 'from huggingface_hub import login; login()'")
        print()
        return 1
    
    # Space configuration
    space_name = "video-profanity-filter"
    repo_id = f"{username}/{space_name}"
    
    print(f"\nSpace name: {space_name}")
    print(f"Full repo ID: {repo_id}")
    print()
    
    # Check if space exists
    try:
        api.repo_info(repo_id, repo_type="space")
        print(f"⚠ Space already exists: {repo_id}")
        print(f"   URL: https://huggingface.co/spaces/{repo_id}")
        response = input("\nDo you want to update it? (y/n): ").strip().lower()
        if response != 'y':
            print("Deployment cancelled.")
            return 0
    except:
        # Create new space
        print("Creating new Space...")
        try:
            create_repo(
                repo_id=repo_id,
                repo_type="space",
                space_sdk="gradio",
                space_hardware="cpu-basic",
                private=False
            )
            print(f"✓ Space created: {repo_id}")
        except Exception as e:
            print(f"✗ Error creating space: {e}")
            return 1
    
    # Files to upload
    files_to_upload = [
        "app.py",
        "gradio_app.py",
        "clean.py",
        "audio_profanity_detector.py",
        "subtitle_processor.py",
        "video_cutter.py",
        "timestamp_merger.py",
        "profanity_words.py",
    ]
    
    # Special handling for requirements.txt
    requirements_file = "requirements_hf.txt"
    if Path(requirements_file).exists():
        # Read and upload as requirements.txt
        print(f"\nUploading {requirements_file} as requirements.txt...")
        upload_file(
            path_or_fileobj=requirements_file,
            path_in_repo="requirements.txt",
            repo_id=repo_id,
            repo_type="space"
        )
        print("✓ requirements.txt uploaded")
    
    # Upload all other files
    print(f"\nUploading {len(files_to_upload)} files...")
    for file in files_to_upload:
        if Path(file).exists():
            print(f"  Uploading {file}...", end=" ")
            try:
                upload_file(
                    path_or_fileobj=file,
                    path_in_repo=file,
                    repo_id=repo_id,
                    repo_type="space"
                )
                print("✓")
            except Exception as e:
                print(f"✗ Error: {e}")
        else:
            print(f"  ✗ {file} not found!")
    
    print()
    print("=" * 60)
    print("DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print(f"\nYour app is being deployed at:")
    print(f"  https://huggingface.co/spaces/{repo_id}")
    print()
    print("Note: First build takes 5-10 minutes.")
    print("      Check the 'Logs' tab in your Space to see progress.")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

