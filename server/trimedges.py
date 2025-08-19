#!/usr/bin/env python3
"""
Video Edge Trimmer

Trims the left and right edges of videos by cropping a specified number of pixels from each side.

Usage:
    python trimedges.py <input_video> <pixels_to_crop> <output_video>

Arguments:
    input_video: Path to the input video file
    pixels_to_crop: Number of pixels to crop from each side (left and right)
    output_video: Path to the output video file

Example:
    python trimedges.py input.mp4 50 output.mp4
    This will crop 50 pixels from the left and 50 pixels from the right.
"""

import sys
import subprocess
import os
from pathlib import Path


def get_video_dimensions(input_file):
    """Get the width and height of the input video."""
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'csv=p=0',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            input_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        width, height = map(int, result.stdout.strip().split(','))
        return width, height
    except subprocess.CalledProcessError as e:
        print(f"Error getting video dimensions: {e}")
        return None, None
    except FileNotFoundError:
        print("Error: ffprobe not found. Please install FFmpeg.")
        return None, None


def trim_video_edges(input_file, pixels_to_crop, output_file):
    """Trim the left and right edges of a video."""
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        return False

    # Get video dimensions
    width, height = get_video_dimensions(input_file)
    if width is None or height is None:
        return False

    # Calculate new dimensions
    pixels_to_crop = int(pixels_to_crop)
    new_width = width - (2 * pixels_to_crop)

    if new_width <= 0:
        print(f"Error: Cropping {pixels_to_crop} pixels from each side would result in zero or negative width.")
        print(f"Original width: {width}, pixels to crop: {pixels_to_crop * 2} total")
        return False

    print(f"Original dimensions: {width}x{height}")
    print(f"Cropping {pixels_to_crop} pixels from each side")
    print(f"New dimensions: {new_width}x{height}")

    # Create output directory if it doesn't exist
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Build FFmpeg command
    # crop filter format: crop=width:height:x:y
    # x=pixels_to_crop (start cropping from x pixels from left)
    # width=new_width (the width after cropping)
    # height=height (keep original height)
    # y=0 (start from top)
    crop_filter = f"crop={new_width}:{height}:{pixels_to_crop}:0"

    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-vf', crop_filter,
        '-c:a', 'copy',  # Copy audio without re-encoding
        '-y',  # Overwrite output file if it exists
        output_file
    ]

    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True)
        print(f"Successfully trimmed video: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error processing video: {e}")
        return False
    except FileNotFoundError:
        print("Error: ffmpeg not found. Please install FFmpeg.")
        return False


def main():
    if len(sys.argv) != 4:
        print("Usage: python trimedges.py <input_video> <pixels_to_crop> <output_video>")
        print("\nArguments:")
        print("  input_video: Path to the input video file")
        print("  pixels_to_crop: Number of pixels to crop from each side (left and right)")
        print("  output_video: Path to the output video file")
        print("\nExample:")
        print("  python trimedges.py input.mp4 50 output.mp4")
        sys.exit(1)

    input_file = sys.argv[1]
    pixels_to_crop = sys.argv[2]
    output_file = sys.argv[3]

    # Validate pixels_to_crop is a number
    try:
        pixels_to_crop = int(pixels_to_crop)
        if pixels_to_crop < 0:
            print("Error: pixels_to_crop must be a positive integer.")
            sys.exit(1)
    except ValueError:
        print("Error: pixels_to_crop must be a valid integer.")
        sys.exit(1)

    # Trim the video
    success = trim_video_edges(input_file, pixels_to_crop, output_file)

    if success:
        print("Video trimming completed successfully!")
        sys.exit(0)
    else:
        print("Video trimming failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
