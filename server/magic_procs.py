from __future__ import annotations

# Standard
import time
import tempfile
import shutil
from pathlib import Path

# Libraries
from flask import Request  # type: ignore
from werkzeug.datastructures import FileStorage  # type: ignore

# Modules
from config import config
import utils


def do_magic(what: str, files: list[FileStorage]) -> tuple[bytes, str] | None:
    try:
        start = time.time()

        if what == "image":
            result = do_image_magic(files[0])
            ext = "jpg"
        elif what == "audio":
            result = do_audio_magic(files[0])
            ext = "mp3"
        elif what == "video":
            result = do_video_magic(files[0])
            ext = "mp4"
        elif what == "album":
            result = do_album_magic(files)
            ext = "mp3"
        elif what == "visual":
            result = do_visual_magic(files)
            ext = "mp4"
        elif what == "gif":
            result = do_gif_magic(files)
            ext = "gif"
        else:
            return None

        end = time.time()
        d = round(end - start, 2)
        utils.log(f"{what} magic took {d} seconds")
    except Exception as e:
        utils.error(e)
        return None

    if not result:
        return None

    return result, f".{ext}"


def is_image_magic(request: Request, file: FileStorage) -> bool:
    if not utils.get_checkbox(request, "image_magic"):
        return False

    return config.image_magic_enabled and utils.is_image_file(file, True)


def is_audio_magic(request: Request, file: FileStorage) -> bool:
    if not utils.get_checkbox(request, "audio_magic"):
        return False

    return config.audio_magic_enabled and utils.is_audio_file(file, True)


def is_video_magic(request: Request, file: FileStorage) -> bool:
    if not utils.get_checkbox(request, "video_magic"):
        return False

    return config.video_magic_enabled and utils.is_video_file(file, True)


def is_album_magic(request: Request, files: list[FileStorage]) -> bool:
    if not utils.get_checkbox(request, "album_magic"):
        return False

    if not config.album_magic_enabled:
        return False

    audio_count = 0

    for file in files:
        if utils.is_audio_file(file):
            audio_count += 1
        else:
            return False

    return audio_count > 1


def is_visual_magic(request: Request, files: list[FileStorage]) -> bool:
    if not utils.get_checkbox(request, "album_magic"):
        return False

    if not config.visual_magic_enabled:
        return False

    img_count = 0
    audio_count = 0

    for file in files:
        if utils.is_image_file(file):
            img_count += 1
        elif utils.is_audio_file(file):
            audio_count += 1
        else:
            return False

    if img_count != 1:
        return False

    return audio_count >= 1


def is_gif_magic(request: Request, files: list[FileStorage]) -> bool:
    if not utils.get_checkbox(request, "gif_magic"):
        return False

    if not config.gif_magic_enabled:
        return False

    img_count = 0

    for file in files:
        if utils.is_image_file(file):
            if utils.is_gif_file(file):
                continue

            img_count += 1
        else:
            return False

    return img_count >= 2


def do_image_magic(file: FileStorage) -> bytes | None:
    content = file.read()

    with (
        tempfile.NamedTemporaryFile(suffix=".jpg") as img_temp,
        tempfile.NamedTemporaryFile(suffix=".jpg") as output_temp,
    ):
        img_temp.write(content)
        img_temp.flush()
        quality = str(config.image_magic_quality) or "6"

        utils.run_cmd(
            [
                "ffmpeg",
                "-i",
                img_temp.name,
                "-qscale:v",
                quality,
                "-y",
                output_temp.name,
            ],
        )

        output_temp.seek(0)
        return output_temp.read()


def do_audio_magic(file: FileStorage) -> bytes | None:
    content = file.read()

    with (
        tempfile.NamedTemporaryFile(suffix=".audio") as audio_temp,
        tempfile.NamedTemporaryFile(suffix=".mp3") as output_temp,
    ):
        audio_temp.write(content)
        audio_temp.flush()
        aq = str(config.audio_magic_quality)

        utils.run_cmd(
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
        )

        output_temp.seek(0)
        return output_temp.read()


def do_video_magic(file: FileStorage) -> bytes | None:
    content = file.read()

    with (
        tempfile.NamedTemporaryFile(suffix=".video") as video_temp,
        tempfile.NamedTemporaryFile(suffix=".mp4") as output_temp,
    ):
        video_temp.write(content)
        video_temp.flush()
        crf = str(config.video_magic_quality) or "28"
        aq = str(config.video_magic_audio_quality) or "0"

        utils.run_cmd(
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
        )

        output_temp.seek(0)
        return output_temp.read()


def do_album_magic(files: list[FileStorage]) -> bytes | None:
    temp_files = []

    try:
        for file in files:
            temp = tempfile.NamedTemporaryFile(suffix=".audio", delete=False)
            temp.write(file.read())
            temp.close()
            file.seek(0)
            temp_files.append(temp.name)

        if not temp_files:
            return None

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", encoding="utf-8"
        ) as list_file:
            for temp_file in temp_files:
                list_file.write(f"file '{temp_file}'\n")

            list_file.flush()
            aq = str(config.audio_magic_quality)

            with tempfile.NamedTemporaryFile(suffix=".mp3") as output_temp:
                utils.run_cmd(
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
                )

                output_temp.seek(0)
                return output_temp.read()
    finally:
        for temp_file in temp_files:
            Path(temp_file).unlink(missing_ok=True)


def do_visual_magic(files: list[FileStorage]) -> bytes | None:
    temp_files = []
    image_file = None

    try:
        for file in files:
            if utils.is_image_file(file):
                image_temp = tempfile.NamedTemporaryFile(suffix=".image", delete=False)
                image_temp.write(file.read())
                image_temp.close()
                file.seek(0)
                image_file = image_temp.name
                break

        for file in files:
            if utils.is_audio_file(file):
                temp = tempfile.NamedTemporaryFile(suffix=".audio", delete=False)
                temp.write(file.read())
                temp.close()
                file.seek(0)
                temp_files.append(temp.name)

        if (not image_file) or (not temp_files):
            return None

        total_duration = 0.0

        for temp_file in temp_files:
            result = utils.run_cmd(
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
            )

            duration = float(result.stdout.strip())
            total_duration += duration

        if not total_duration:
            return None

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", encoding="utf-8"
        ) as list_file:
            for temp_file in temp_files:
                list_file.write(f"file '{temp_file}'\n")

            list_file.flush()

            with tempfile.NamedTemporaryFile(suffix=".mp4") as output_temp:
                w = str(config.visual_magic_width) or "640"
                h = str(config.visual_magic_height) or "480"
                crf = str(config.visual_magic_video_quality) or "28"
                bg = str(config.visual_magic_color) or "black"
                aq = str(config.visual_magic_audio_quality) or "0"

                utils.run_cmd(
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
                        "-map",
                        "0:a",
                        "-map",
                        "1:v",
                        "-c:v",
                        "libx264",
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
                )

                output_temp.seek(0)
                return output_temp.read()
    finally:
        for temp_file in temp_files:
            Path(temp_file).unlink(missing_ok=True)
        if image_file:
            Path(image_file).unlink(missing_ok=True)


def do_gif_magic(files: list[FileStorage]) -> bytes | None:
    temp_dir = tempfile.mkdtemp()

    try:
        for i, file in enumerate(files):
            content = file.read()
            file.seek(0)

            input_path = Path(temp_dir) / f"input_{i}.tmp"
            output_path = Path(temp_dir) / f"frame_{i:04d}.png"

            # Write content to temp file
            with input_path.open("wb") as f:
                f.write(content)

            # Convert to PNG
            utils.run_cmd(
                [
                    "ffmpeg",
                    "-i",
                    str(input_path),
                    "-frames:v",
                    "1",
                    "-y",
                    str(output_path),
                ]
            )

            # Clean up temporary input file
            input_path.unlink()

        # Create GIF from PNG files
        gif_path = Path(temp_dir) / "output.gif"
        w = str(config.gif_magic_width or "640")
        h = str(config.gif_magic_height or "480")
        fps = str(config.gif_magic_fps) or "2"
        bg = str(config.gif_magic_color) or "black"

        utils.run_cmd(
            [
                "ffmpeg",
                "-framerate",
                fps,
                "-i",
                str(Path(temp_dir) / "frame_%04d.png"),
                "-vf",
                f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color={bg}",
                "-y",
                str(gif_path),
            ]
        )

        # Read the GIF content
        with gif_path.open("rb") as gif_file:
            return gif_file.read()
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
