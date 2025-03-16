from __future__ import annotations

# Standard
import subprocess
import tempfile
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
    temp_files = []
    list_file_path = None

    try:
        for file in files:
            temp = tempfile.NamedTemporaryFile(
                suffix=".jpg", delete=False, encoding="utf-8"
            )

            temp.write(file.read())
            temp.close()
            file.seek(0)
            temp_files.append(temp.name)

        if not temp_files:
            return None

        list_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        )

        list_file_path = list_file.name

        frame_duration = getattr(config, "gif_magic_frame_duration", 0.2)

        for temp_file in temp_files:
            list_file.write(f"file '{temp_file}'\n")
            list_file.write(f"duration {frame_duration}\n")

        list_file.write(f"file '{temp_files[-1]}'\n")
        list_file.close()

        with tempfile.NamedTemporaryFile(suffix=".gif") as output_temp:
            width = str(config.gif_magic_width) or "640"
            bg_color = str(config.gif_magic_color) or "black"

            cmd = [
                "ffmpeg",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                list_file_path,
                "-vf",
                f"scale={width}:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse,format=rgba,pad=iw:ih:(ow-iw)/2:(oh-ih)/2:color={bg_color}@1",
                "-loop",
                "0",
                "-threads",
                "0",
                "-y",
                output_temp.name,
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            _, _ = process.communicate()

            if process.returncode != 0:
                return None

            output_temp.seek(0)
            return output_temp.read()
    finally:
        for temp_file in temp_files:
            Path(temp_file).unlink(missing_ok=True)
        if list_file_path:
            Path(list_file_path).unlink(missing_ok=True)
