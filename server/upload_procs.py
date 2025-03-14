from __future__ import annotations

# Standard
import zipfile
import hashlib
import mimetypes
import subprocess
import tempfile
import time
from typing import Any
from pathlib import Path
from io import BytesIO

# Libraries
import ulid  # type: ignore
from flask import Request  # type: ignore
from werkzeug.datastructures import FileStorage  # type: ignore

# Modules
import utils
import database
from config import config
import post_procs
import user_procs
from user_procs import User


def error(s: str) -> tuple[bool, str]:
    return False, f"Error: {s}"


def get_name(user: User) -> str:
    u = ulid.new()
    name = str(u.str)[: config.get_post_name_length()].strip()

    if user.mark:
        name = f"{name}_{user.mark}".strip()

    if not config.uppercase_names:
        name = name.lower()

    return name


def make_zip(files: list[FileStorage]) -> bytes:
    buffer = BytesIO()
    clevel = config.compression_level
    fixed_time = (1980, 1, 1, 0, 0, 0)

    with zipfile.ZipFile(
        buffer, "w", zipfile.ZIP_DEFLATED, compresslevel=clevel
    ) as zipf:
        for file in sorted(files, key=lambda f: f.filename):
            content = file.read()
            filename = Path(file.filename).name
            zip_info = zipfile.ZipInfo(filename)
            zip_info.date_time = fixed_time
            zip_info.comment = b""
            zip_info.extra = b""
            zip_info.create_system = 0
            zip_info.create_version = 20
            zip_info.extract_version = 20
            zip_info.external_attr = 0
            zipf.writestr(zip_info, content)
            file.seek(0)

    buffer.seek(0)
    return buffer.getvalue()


def check_hash(content: bytes) -> tuple[str, str]:
    file_hash = hashlib.sha256(content).hexdigest()

    if not config.allow_same_hash:
        existing = database.get_posts(file_hash=file_hash)

        if existing:
            return "", existing[0].name

    return file_hash, ""


def upload(request: Any, user: User, mode: str = "normal") -> tuple[bool, str]:
    if not user:
        return error("No user")

    title = request.form.get("title", "")

    if len(title) > config.max_title_length:
        return error("Title is too long")

    if mode == "cli":
        u_ok, u_msg = user_procs.check_user_limit(user)

        if not u_ok:
            return error(u_msg)

    files = []
    seen_files = set()

    for file in request.files.getlist("file"):
        if file and file.filename:
            filename = Path(file.filename).name

            if filename and (filename not in seen_files):
                seen_files.add(filename)
                files.append(file)

    if (len(files) < 1) or (len(files) > config.max_upload_files):
        return error("Wrong file length")

    total_size = 0

    for file in files:
        if not file.name:
            return error("No file name")

        if len(file.name) > 255:
            return error("File name is too long")

        if not hasattr(file, "read"):
            return error("File object has no 'read' attribute")

        file.seek(0, 2)
        total_size += file.tell()
        file.seek(0)

    if not user_procs.check_user_max(user, total_size):
        return error("Upload is too big")

    post_name = get_name(user)
    audiomagic = False
    privacy = request.form.get("privacy", "public")

    if privacy not in ["public", "private"]:
        return error("Invalid privacy setting")

    makemode = request.form.get("makemode", "normal")
    compress = makemode == "zip"

    if len(files) > 1:
        if (
            (len(files) == 2)
            and user.mage
            and makemode == "audiomagic"
            and config.audiomagic_enabled
            and is_audiomagic(files)
        ):
            audiomagic = True
        else:
            compress = True

    if compress:
        try:
            content = make_zip(files)
            original = ""
            ext = ".zip"

        except Exception as e:
            utils.error(e)
            return error("Failed to compress files")
    elif audiomagic:
        try:
            start = time.time()
            result = make_audiomagic(files)
            end = time.time()
            d = round(end - start, 2)
            utils.q(f"Audio image took {d} seconds")

            if not result:
                return error("Failed to make audiomagic")

            content = result
            original = ""
            ext = ".mp4"

            if not content:
                return error("Failed to make audiomagic")
        except Exception as e:
            utils.error(e)
            return error("Failed to make audiomagic")
    else:
        file = files[0]
        content = file.read()
        original = utils.clean_filename(Path(file.filename).stem)
        ext = Path(file.filename).suffix

    file_hash, existing = check_hash(content)

    if existing and (privacy == "public"):
        if mode == "normal":
            return True, existing

        return True, f"post/{existing}"

    try:
        if ext:
            full_name = post_name + ext
        else:
            full_name = post_name

        path = utils.files_dir() / Path(full_name)
        path.write_bytes(content)
    except Exception as e:
        utils.error(e)
        return error("Failed to save file")

    file_size = path.stat().st_size
    mtype, _ = mimetypes.guess_type(path)
    mtype = mtype or ""

    database.add_post(
        user_id=user.id,
        name=post_name,
        ext=path.suffix[1:],
        title=title,
        original=original,
        mtype=mtype,
        size=file_size,
        file_hash=file_hash,
        privacy=privacy,
    )

    if config.samples_enabled:
        try:
            if compress:
                get_zip_sample(path, files)
            elif mtype.startswith("image"):
                get_image_sample(path)
            elif mtype.startswith("video"):
                get_video_sample(path)
            elif mtype.startswith("audio"):
                get_audio_sample(path)
            elif utils.is_text_file(path):
                get_text_sample(path)
        except Exception as e:
            get_text_sample(path)
            utils.error(e)

    database.update_user_last_date(user.id)
    post_procs.check_storage()

    if mode == "normal":
        return True, post_name

    return True, f"post/{post_name}"


def api_upload(request: Request) -> tuple[bool, str]:
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    if (not username) or (not password):
        return error("Missing username or password")

    if (len(username) > 255) or (len(password) > 255):
        return error("Invalid username or password")

    user = user_procs.check_auth(username, password)

    if not user:
        return error("Invalid username or password")

    return upload(request, user, "cli")


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


def is_audiomagic(files: list[FileStorage]) -> bool:
    imgs = utils.image_exts()
    audio = utils.audio_exts()

    if len(files) != 2:
        return False

    f1 = Path(files[0].filename).suffix[1:].lower()
    f2 = Path(files[1].filename).suffix[1:].lower()
    return (f1 in imgs and f2 in audio) or (f2 in imgs and f1 in audio)


def make_audiomagic(files: list[FileStorage]) -> bytes | None:
    img_file = None
    audio_file = None

    for file in files:
        if Path(file.filename).suffix[1:].lower() in utils.image_exts():
            img_file = file
        elif Path(file.filename).suffix[1:].lower() in utils.audio_exts():
            audio_file = file

    if not img_file or not audio_file:
        return None

    img_content = img_file.read()
    audio_content = audio_file.read()

    with (
        tempfile.NamedTemporaryFile(suffix=".jpg") as img_temp,
        tempfile.NamedTemporaryFile(suffix=".mp3") as audio_temp,
        tempfile.NamedTemporaryFile(suffix=".mp4") as output_temp,
    ):
        img_temp.write(img_content)
        img_temp.flush()

        audio_temp.write(audio_content)
        audio_temp.flush()
        w = config.audiomagic_width
        h = config.audiomagic_height
        crf = config.audiomagic_video_quality
        bg = config.audiomagic_color or "black"

        process = subprocess.Popen(
            [
                "ffmpeg",
                "-loop",
                "1",
                "-i",
                img_temp.name,
                "-i",
                audio_temp.name,
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-tune",
                "stillimage",
                "-crf",
                f"{crf}",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "libmp3lame",
                "-b:a",
                f"{config.audiomagic_audio_bitrate}k",
                "-vf",
                f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color={bg}",
                "-shortest",
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
