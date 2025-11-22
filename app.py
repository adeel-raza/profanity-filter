"""
Hugging Face Spaces Entry Point
This file is used when deploying to Hugging Face Spaces
"""

from gradio_app import create_interface

# Create and launch the interface
demo = create_interface()

if __name__ == "__main__":
    demo.launch()

