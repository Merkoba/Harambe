from __future__ import annotations

# Standard
import zipfile
import hashlib
import mimetypes
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
import post_procs
import user_procs
import magic_procs
import sample_procs
from config import config
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
    clevel = config.zip_level
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
    privacy = request.form.get("privacy", "public")

    if privacy not in ["public", "private"]:
        return error("Invalid privacy setting")

    original = utils.clean_filename(Path(files[0].filename).stem)
    zip_archive = utils.get_checkbox(request, "zip")

    image_magic = False
    audio_magic = False
    video_magic = False
    album_magic = False
    visual_magic = False
    gif_magic = False

    if len(files) == 1:
        if config.magic_enabled:
            if magic_procs.is_image_magic(request, files[0]):
                image_magic = True
            elif magic_procs.is_audio_magic(request, files[0]):
                audio_magic = True
            elif magic_procs.is_video_magic(request, files[0]):
                video_magic = True
    elif len(files) > 1:
        if (
            user.mage
            and config.magic_enabled
            and magic_procs.is_album_magic(request, files)
        ):
            album_magic = True
        elif (
            user.mage
            and config.magic_enabled
            and magic_procs.is_visual_magic(request, files)
        ):
            visual_magic = True
        elif (
            user.mage
            and config.magic_enabled
            and magic_procs.is_gif_magic(request, files)
        ):
            gif_magic = True
        else:
            zip_archive = True

    if (
        image_magic
        or audio_magic
        or video_magic
        or album_magic
        or visual_magic
        or gif_magic
    ):
        zip_archive = False

    if zip_archive:
        try:
            content = make_zip(files)
            ext = ".zip"

        except Exception as e:
            utils.error(e)
            return error("Failed to zip files")
    elif image_magic:
        result = magic_procs.do_magic("image", files)

        if not result:
            return error("Failed to do image magic")

        content, ext = result
    elif audio_magic:
        result = magic_procs.do_magic("audio", files)

        if not result:
            return error("Failed to do audio magic")

        content, ext = result
    elif video_magic:
        result = magic_procs.do_magic("video", files)

        if not result:
            return error("Failed to do video magic")

        content, ext = result
    elif album_magic:
        result = magic_procs.do_magic("album", files)

        if not result:
            return error("Failed to do album magic")

        content, ext = result
    elif visual_magic:
        result = magic_procs.do_magic("visual", files)

        if not result:
            return error("Failed to do visual magic")

        content, ext = result
    elif gif_magic:
        result = magic_procs.do_magic("gif", files)

        if not result:
            return error("Failed to do gif magic")

        content, ext = result
    else:
        file = files[0]
        content = file.read()
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
        sample_procs.make_sample(path, files, mtype, zip_archive)

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
