# Standard
import subprocess
from pathlib import Path

# Libraries
from werkzeug.datastructures import FileStorage  # type: ignore

# Modules
import utils
from config import config


def get_video_sample(path: Path) -> None:
    sample_name = f"{path.stem}.jpg"
    sample_path = utils.samples_dir() / Path(sample_name)

    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            path,
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    duration = float(result.stdout.strip())
    middle_point = duration / 2
    time_str = str(middle_point)
    tw = config.sample_width
    th = config.sample_height
    tc = config.sample_color = "black"
    scale = f"scale={tw}:{th}:force_original_aspect_ratio=decrease,pad={tw}:{th}:({tw}-iw)/2:({th}-ih)/2:color={tc}"
    quality = str(config.sample_quality_image)

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            time_str,
            "-i",
            str(path),
            "-vframes",
            "1",
            "-vf",
            scale,
            "-q:v",
            quality,
            "-an",
            "-threads",
            "0",
            sample_path,
        ],
        check=True,
    )


def get_image_sample(path: Path) -> None:
    sample_name = f"{path.stem}.jpg"
    sample_path = utils.samples_dir() / Path(sample_name)

    tw = config.sample_width
    th = config.sample_height
    tc = config.sample_color or "black"
    scale = f"scale={tw}:{th}:force_original_aspect_ratio=decrease,pad={tw}:{th}:({tw}-iw)/2:({th}-ih)/2:color={tc}"
    quality = str(config.sample_quality_image)

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(path),
            "-vf",
            scale,
            "-q:v",
            quality,
            "-threads",
            "0",
            sample_path,
        ],
        check=True,
    )


def get_audio_sample(path: Path) -> None:
    sample_name = f"{path.stem}.jpg"
    sample_path = utils.samples_dir() / Path(sample_name)
    sample_name = f"{path.stem}.mp3"
    sample_path = utils.samples_dir() / Path(sample_name)

    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            path,
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    duration = float(result.stdout.strip())
    sample_duration = min(10.0, duration)
    quality = str(config.sample_quality_audio)

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(path),
            "-t",
            str(sample_duration),
            "-acodec",
            "libmp3lame",
            "-q:a",
            quality,
            "-threads",
            "0",
            sample_path,
        ],
        check=True,
    )


def get_text_sample(path: Path) -> None:
    sample_name = f"{path.stem}.txt"
    sample_path = utils.samples_dir() / Path(sample_name)
    max_bytes = config.sample_text_bytes

    with path.open("r") as file:
        sample_content = file.read(max_bytes).strip()

    sample_path.write_text(sample_content)


def get_zip_sample(path: Path, files: list[FileStorage]) -> None:
    sample = "\n".join([Path(file.filename).name for file in files])
    sample = sample[: config.sample_zip_chars].strip()
    sample_name = f"{path.stem}.txt"
    sample_path = utils.samples_dir() / Path(sample_name)
    sample_path.write_text(sample)
