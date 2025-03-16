from __future__ import annotations

# Standard
import subprocess
import tempfile
import shutil
from pathlib import Path

# Libraries
from flask import Request  # type: ignore
from werkzeug.datastructures import FileStorage  # type: ignore

# Modules
from config import config
import utils


def is_image_magic(request: Request, file: FileStorage) -> bool:
    if not utils.get_checkbox(request, "image_magic"):
        return False

    return config.image_magic_enabled and file.content_type.startswith("image/")


def is_audio_magic(request: Request, file: FileStorage) -> bool:
    if not utils.get_checkbox(request, "audio_magic"):
        return False

    return config.audio_magic_enabled and file.content_type.startswith("audio/")


def is_video_magic(request: Request, file: FileStorage) -> bool:
    if not utils.get_checkbox(request, "video_magic"):
        return False

    return config.video_magic_enabled and file.content_type.startswith("video/")


def is_album_magic(request: Request, files: list[FileStorage]) -> bool:
    if not utils.get_checkbox(request, "album_magic"):
        return False

    if not config.album_magic_enabled:
        return False

    img_count = 0
    audio_count = 0

    for file in files:
        if file.content_type.startswith("image/"):
            img_count += 1
        elif file.content_type.startswith("audio/"):
            audio_count += 1
        else:
            return False

    if img_count > 1:
        return False

    if img_count == 1:
        return audio_count >= 1

    if img_count == 0:
        return audio_count > 1

    return False


def is_gif_magic(request: Request, files: list[FileStorage]) -> bool:
    if not utils.get_checkbox(request, "gif_magic"):
        return False

    if not config.gif_magic_enabled:
        return False

    img_count = 0

    for file in files:
        if file.content_type.startswith("image/"):
            img_count += 1
        else:
            return False

    return img_count >= 2


def make_image_magic(file: FileStorage) -> bytes | None:
    content = file.read()

    with (
        tempfile.NamedTemporaryFile(suffix=".jpg") as img_temp,
        tempfile.NamedTemporaryFile(suffix=".jpg") as output_temp,
    ):
        img_temp.write(content)
        img_temp.flush()
        quality = str(config.image_magic_quality) or "6"

        process = subprocess.Popen(
            [
                "ffmpeg",
                "-i",
                img_temp.name,
                "-qscale:v",
                quality,
                "-y",
                output_temp.name,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        _, _ = process.communicate()

        if process.returncode != 0:
            return None

        output_temp.seek(0)
        return output_temp.read()


def make_audio_magic(file: FileStorage) -> bytes | None:
    content = file.read()

    with (
        tempfile.NamedTemporaryFile(suffix=".audio") as audio_temp,
        tempfile.NamedTemporaryFile(suffix=".mp3") as output_temp,
    ):
        audio_temp.write(content)
        audio_temp.flush()
        aq = str(config.audio_magic_quality)

        process = subprocess.Popen(
            [
                "ffmpeg",
                "-i",
                audio_temp.name,
                "-c:a",
                "libmp3lame",
                "-q:a",
                aq,
                "-threads",
                "0",
                "-y",
                output_temp.name,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        _, _ = process.communicate()

        if process.returncode != 0:
            return None

        output_temp.seek(0)
        return output_temp.read()


def make_video_magic(file: FileStorage) -> bytes | None:
    content = file.read()

    with (
        tempfile.NamedTemporaryFile(suffix=".video") as video_temp,
        tempfile.NamedTemporaryFile(suffix=".mp4") as output_temp,
    ):
        video_temp.write(content)
        video_temp.flush()
        crf = str(config.video_magic_quality) or "28"
        aq = str(config.video_magic_audio_quality) or "0"

        process = subprocess.Popen(
            [
                "ffmpeg",
                "-i",
                video_temp.name,
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                crf,
                "-c:a",
                "libmp3lame",
                "-q:a",
                aq,
                "-movflags",
                "+faststart",
                "-threads",
                "0",
                "-y",
                output_temp.name,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        _, _ = process.communicate()

        if process.returncode != 0:
            return None

        output_temp.seek(0)
        return output_temp.read()


def make_album_magic(files: list[FileStorage]) -> tuple[bytes, str] | tuple[None, str]:
    temp_files = []
    image_file = None

    try:
        for file in files:
            if file.content_type.startswith("image/"):
                image_temp = tempfile.NamedTemporaryFile(suffix=".image", delete=False)
                image_temp.write(file.read())
                image_temp.close()
                file.seek(0)
                image_file = image_temp.name
                break

        for file in files:
            if file.content_type.startswith("audio/"):
                temp = tempfile.NamedTemporaryFile(suffix=".audio", delete=False)
                temp.write(file.read())
                temp.close()
                file.seek(0)
                temp_files.append(temp.name)

        if not temp_files:
            return None, ""

        total_duration = 0.0

        for temp_file in temp_files:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    temp_file,
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            duration = float(result.stdout.strip())
            total_duration += duration

        if not total_duration:
            return None, ""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", encoding="utf-8"
        ) as list_file:
            for temp_file in temp_files:
                list_file.write(f"file '{temp_file}'\n")

            list_file.flush()
            aq = str(config.audio_magic_quality)

            if image_file:
                with tempfile.NamedTemporaryFile(suffix=".mp4") as output_temp:
                    w = str(config.album_magic_width) or "640"
                    h = str(config.album_magic_height) or "480"
                    crf = str(config.album_magic_video_quality) or "28"
                    bg = str(config.album_magic_color) or "black"

                    process = subprocess.Popen(
                        [
                            "ffmpeg",
                            "-f",
                            "concat",
                            "-safe",
                            "0",
                            "-i",
                            list_file.name,
                            "-loop",
                            "1",
                            "-i",
                            image_file,
                            "-c:v",
                            "libx264",
                            "-preset",
                            "medium",
                            "-tune",
                            "stillimage",
                            "-crf",
                            f"{crf}",
                            "-c:a",
                            "libmp3lame",
                            "-q:a",
                            aq,
                            "-pix_fmt",
                            "yuv420p",
                            "-vf",
                            f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color={bg}",
                            "-t",
                            str(total_duration),
                            "-threads",
                            "0",
                            "-y",
                            output_temp.name,
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )

                    _, _ = process.communicate()

                    if process.returncode != 0:
                        return None, ""

                    output_temp.seek(0)
                    return output_temp.read(), "mp4"
            else:
                with tempfile.NamedTemporaryFile(suffix=".mp3") as output_temp:
                    process = subprocess.Popen(
                        [
                            "ffmpeg",
                            "-f",
                            "concat",
                            "-safe",
                            "0",
                            "-i",
                            list_file.name,
                            "-c:a",
                            "libmp3lame",
                            "-q:a",
                            aq,
                            "-threads",
                            "0",
                            "-y",
                            output_temp.name,
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )

                    _, _ = process.communicate()

                    if process.returncode != 0:
                        return None, ""

                    output_temp.seek(0)
                    return output_temp.read(), "mp3"
    finally:
        for temp_file in temp_files:
            Path(temp_file).unlink(missing_ok=True)
        if image_file:
            Path(image_file).unlink(missing_ok=True)


def make_gif_magic(files: list[FileStorage]) -> bytes | None:
    temp_dir = None

    try:
        temp_dir = tempfile.mkdtemp()

        if not files:
            return None

        for i, file in enumerate(files):
            temp_path = Path(temp_dir) / f"image_{i:03d}.png"

            with temp_path.open("wb") as f:
                f.write(file.read())

            file.seek(0)

        width = str(config.gif_magic_width) or "640"
        height = str(config.gif_magic_height) or "480"
        fps = str(config.gif_magic_fps) or "2"

        with tempfile.NamedTemporaryFile(suffix=".gif") as output_temp:
            for i in range(len(files)):
                input_path = Path(temp_dir) / f"image_{i:03d}.png"
                output_path = Path(temp_dir) / f"scaled_{i:03d}.png"

                pre_cmd = [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(input_path),
                    "-vf",
                    f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black",
                    str(output_path),
                ]

                process = subprocess.run(pre_cmd, capture_output=True, check=True)

                if process.returncode != 0:
                    return None

            palette_file = Path(temp_dir) / "palette.png"
            palette_cmd = [
                "ffmpeg",
                "-y",
                "-framerate",
                fps,
                "-pattern_type",
                "glob",
                "-i",
                f"{temp_dir}/scaled_*.png",
                "-vf",
                "palettegen=stats_mode=diff",
                str(palette_file),
            ]

            process = subprocess.run(palette_cmd, capture_output=True, check=True)

            if process.returncode != 0:
                return None

            cmd = [
                "ffmpeg",
                "-y",
                "-framerate",
                fps,
                "-pattern_type",
                "glob",
                "-i",
                f"{temp_dir}/scaled_*.png",
                "-i",
                str(palette_file),
                "-filter_complex",
                "paletteuse=dither=bayer:bayer_scale=5",
                "-loop",
                "0",
                output_temp.name,
            ]

            process = subprocess.run(cmd, capture_output=True, check=True)

            if process.returncode != 0:
                return None

            output_temp.seek(0)
            return output_temp.read()
    finally:
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
