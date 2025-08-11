# Standard
from pathlib import Path
from typing import Callable
from subprocess import CompletedProcess

# Libraries
from werkzeug.datastructures import FileStorage  # type: ignore

# Modules
import utils
from config import config


def sample_exists(path: Path) -> bool:
    for sample in utils.samples_dir().iterdir():
        if sample.stem == path.stem:
            return True

    return False


def make_sample(
    path: Path, files: list[FileStorage], mtype: str, zip_archive: bool
) -> None:
    if sample_exists(path):
        return

    try:
        if zip_archive:
            get_zip_sample(path, files)
        elif mtype.startswith("image"):
            if mtype == "image/gif":
                get_gif_sample(path)
            else:
                get_image_sample(path)
        elif mtype.startswith("video"):
            get_video_sample(path)
        elif mtype.startswith("audio"):
            get_audio_sample(path)
        elif utils.is_text_file(path):
            get_text_sample(path)
        else:
            get_application_sample(path, files)
    except Exception:
        try:
            utils.error("Failed to get sample #1")
            get_text_sample(path)
        except Exception:
            utils.error("Failed to get sample #2")


def get_video_sample(path: Path) -> None:
    sample_name = f"{path.stem}.jpg"
    sample_path = utils.samples_dir() / Path(sample_name)

    # Ensure the samples directory exists
    utils.samples_dir().mkdir(parents=True, exist_ok=True)

    try:
        result = utils.run_cmd(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
        )

        duration = float(result.stdout.strip())
        # For very short videos or single-frame videos, use the first frame
        time_str = "0" if duration < 0.1 else str(duration / 2)
    except Exception:
        # If duration can't be determined, default to the first frame
        time_str = "0"

    tw = config.sample_width
    th = config.sample_height
    tc = config.sample_color or "black"
    scale = f"scale={tw}:{th}:force_original_aspect_ratio=decrease,pad={tw}:{th}:({tw}-iw)/2:({th}-ih)/2:color={tc}"
    quality = str(config.sample_quality_image)

    # Try multiple strategies to extract a frame, starting with the most likely to succeed
    methods: list[Callable[[], CompletedProcess[str]]] = [
        # Standard approach with timestamp
        lambda: utils.run_cmd(
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
                str(sample_path),
            ]
        ),
        # First frame without timestamp
        lambda: utils.run_cmd(
            [
                "ffmpeg",
                "-y",
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
                str(sample_path),
            ]
        ),
        # Simplest approach - first frame with minimal options
        lambda: utils.run_cmd(
            [
                "ffmpeg",
                "-y",
                "-ss",
                "0",
                "-i",
                str(path),
                "-vframes",
                "1",
                "-f",
                "image2",
                str(sample_path),
            ]
        ),
        # More robust approach for problematic videos
        lambda: utils.run_cmd(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(path),
                "-vf",
                f"thumbnail,{scale}",
                "-q:v",
                quality,
                "-frames:v",
                "1",
                "-threads",
                "0",
                str(sample_path),
            ]
        ),
        # Ultimate fallback - create a color image
        lambda: utils.run_cmd(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"color=c={tc}:s={tw}x{th}",
                "-frames:v",
                "1",
                str(sample_path),
            ]
        ),
    ]

    for method in methods:
        try:
            method()
        except Exception:
            continue
        # Check if file was actually created
        if sample_path.exists() and sample_path.stat().st_size > 0:
            return  # Success!


def get_image_sample(path: Path) -> None:
    sample_name = f"{path.stem}.jpg"
    sample_path = utils.samples_dir() / Path(sample_name)

    tw = config.sample_width
    th = config.sample_height
    tc = config.sample_color or "black"
    scale = f"scale={tw}:{th}:force_original_aspect_ratio=decrease,pad={tw}:{th}:({tw}-iw)/2:({th}-ih)/2:color={tc}"
    quality = str(config.sample_quality_image)

    utils.run_cmd(
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
            str(sample_path),
        ],
    )


def get_gif_sample(path: Path) -> None:
    sample_name = f"{path.stem}.jpg"
    sample_path = utils.samples_dir() / Path(sample_name)

    tw = config.sample_width
    th = config.sample_height
    tc = config.sample_color or "black"
    scale = f"scale={tw}:{th}:force_original_aspect_ratio=decrease,pad={tw}:{th}:({tw}-iw)/2:({th}-ih)/2:color={tc}"
    quality = str(config.sample_quality_image)

    utils.run_cmd(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(path),
            "-vframes",
            "1",
            "-vf",
            scale,
            "-q:v",
            quality,
            "-threads",
            "0",
            str(sample_path),
        ],
    )


def get_audio_sample(path: Path) -> None:
    sample_name = f"{path.stem}.jpg"
    sample_path = utils.samples_dir() / Path(sample_name)
    sample_name = f"{path.stem}.mp3"
    sample_path = utils.samples_dir() / Path(sample_name)

    result = utils.run_cmd(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
    )

    duration = float(result.stdout.strip())
    sample_duration = min(10.0, duration)
    quality = str(config.sample_quality_audio)

    utils.run_cmd(
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
            str(sample_path),
        ],
    )


def get_text_sample(path: Path) -> None:
    sample_name = f"{path.stem}.txt"
    sample_path = utils.samples_dir() / Path(sample_name)
    max_bytes = config.sample_text_bytes

    with path.open("r") as file:
        sample_content = file.read(max_bytes)

    sample_path.write_text(sample_content)


def get_zip_sample(path: Path, files: list[FileStorage]) -> None:
    lines = []

    for file in files:
        filename = Path(file.filename).name
        line = filename

        try:
            size = 0

            if hasattr(file, "content_length") and file.content_length is not None:
                size = file.content_length

            if (size == 0) and hasattr(file, "stream"):
                try:
                    current_pos = file.stream.tell()

                    if hasattr(file.stream, "seekable") and file.stream.seekable():
                        file.stream.seek(0, 2)
                        size = file.stream.tell()
                        file.stream.seek(current_pos)
                except Exception:
                    pass

            if size > 0:
                if size < 1024:
                    size_str = f"{size} b"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.1f} kb"
                elif size < 1024 * 1024 * 1024:
                    size_str = f"{size / (1024 * 1024):.1f} mb"
                elif size < 1024 * 1024 * 1024 * 1024:
                    size_str = f"{size / (1024 * 1024 * 1024):.1f} gb"
                else:
                    size_str = f"{size / (1024 * 1024 * 1024 * 1024):.1f} tb"

                line = f"{filename} | {size_str}"
        except Exception as e:
            utils.error(e)

        lines.append(line)

    sample = "\n".join(lines)
    sample = sample[: config.sample_zip_chars].strip()
    sample_name = f"{path.stem}.txt"
    sample_path = utils.samples_dir() / Path(sample_name)
    sample_path.write_text(sample)


def get_application_sample(path: Path, files: list[FileStorage]) -> None:
    names = []

    for file in files:
        filename = Path(file.filename).name
        names.append(filename)

    sample = "\n".join(names)
    sample_name = f"{path.stem}.txt"
    sample_path = utils.samples_dir() / Path(sample_name)
    sample_path.write_text(sample)


def save_presample(path: Path, presample: bytes, presample_ext: str) -> None:
    sample_name = f"{path.stem}.{presample_ext}"
    sample_path = utils.samples_dir() / Path(sample_name)
    sample_path.write_bytes(presample)
