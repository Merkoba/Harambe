from __future__ import annotations

# Standard
import zipfile
import hashlib
import mimetypes
from typing import Any
from pathlib import Path
from io import BytesIO

# Libraries
from flask import Request  # type: ignore
import ulid  # type: ignore

# Modules
import utils
import database
from config import config
import post_procs
import user_procs
from user_procs import User


def error(s: str) -> tuple[bool, str]:
    return False, f"Error: {s}"


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

    files = request.files.getlist("file")

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

    def get_name() -> str:
        u = ulid.new()
        name = str(u.str)[: config.get_post_name_length()].strip()

        if user.mark:
            name = f"{name}_{user.mark}".strip()

        if not config.uppercase_names:
            name = name.lower()

        return name

    post_name = get_name()

    def make_zip() -> BytesIO:
        zip_buffer = BytesIO()
        clevel = config.compression_level

        with zipfile.ZipFile(
            zip_buffer, "w", zipfile.ZIP_DEFLATED, compresslevel=clevel
        ) as zipf:
            for file in files:
                content = file.read()
                filename = Path(file.filename).name
                zipf.writestr(filename, content)
                file.seek(0)

        zip_buffer.seek(0)
        return zip_buffer

    def check_hash(content: BytesIO | Buffer) -> tuple[str, str]:
        file_hash = hashlib.sha256(content).hexdigest()

        if not config.allow_same_hash:
            existing = database.get_posts(file_hash=file_hash)

            if existing:
                return "", existing[0].name

        return file_hash, ""

    compress = request.form.get("compress", "off") == "on"
    original = ""
    sample = ""

    if len(files) > 1:
        compress = True

    if compress:
        try:
            content = make_zip()
        except Exception as e:
            utils.error(e)
            return error("Failed to compress files")
    else:
        content = file.read()
        original = utils.clean_filename(Path(files[0].filename).stem)

    file_hash, existing = check_hash(content)

    if existing:
        if mode == "normal":
            return file_hash, existing

        return file_hash, f"post/{existing}"

    try:
        ext = Path(file.filename).suffix

        if ext:
            full_name = post_name + ext
        else:
            full_name = post_name

        path = Path(full_name)

        if compress:
            with path.open("wb") as f:
                f.write(content.getvalue())
        else:
            file.save(path)
    except Exception as e:
        utils.error(e)
        return error("Failed to save file")

    file_size = path.stat().st_size
    mtype, _ = mimetypes.guess_type(path)
    mtype = mtype or ""

    if mtype.startswith("text"):
        sample = content[: config.sample_size].decode("utf-8", errors="ignore").strip()

    database.add_post(
        user_id=user.id,
        name=post_name,
        ext=path.suffix[1:],
        title=title,
        original=original,
        mtype=mtype,
        size=file_size,
        sample=sample,
        file_hash=file_hash,
    )

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
