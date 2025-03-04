from __future__ import annotations

# Standard
import zipfile
import hashlib
import mimetypes
from typing import Any
from pathlib import Path

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

    file = request.files.get("file", None)

    if not file:
        return error("No file")

    if not file.name:
        return error("No file name")

    if len(file.name) > 255:
        return error("File name is too long")

    if hasattr(file, "read"):
        try:
            file.seek(0, 2)
            size = file.tell()
            file.seek(0)

            if not user_procs.check_user_max(user, size):
                return error("File is too big")

            content = file.read()

            if content:
                file_hash = hashlib.sha256(content).hexdigest()
                existing = database.get_posts(file_hash=file_hash)

                if existing:
                    first = existing[0]

                    if mode == "normal":
                        return True, first.name

                    return True, f"post/{first.name}"

                file.seek(0)
                fname = file.filename
                pfile = Path(fname)
                ext = pfile.suffix.lower()
                name = pfile.stem
                u = ulid.new()
                name = u.str[: config.get_post_name_length()]

                if user.mark:
                    name = f"{name}_{user.mark}".strip()

                if not config.uppercase_names:
                    name = name.lower()

                try:
                    if ext:
                        full_name = f"{name}{ext}"
                    else:
                        full_name = name

                    path = utils.files_dir() / full_name

                    if request.form.get("compress", "off") == "on":
                        zip_path = path.with_suffix(".zip")
                        clevel = config.compression_level

                        with zipfile.ZipFile(
                            zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=clevel
                        ) as zipf:
                            zipf.writestr(path.name, content)
                            file_size = zip_path.stat().st_size
                            path = zip_path
                    else:
                        file.save(path)
                        file_size = path.stat().st_size

                    if config.allow_titles:
                        title = utils.clean_title(title)
                    else:
                        title = ""

                    mtype, _ = mimetypes.guess_type(path)
                    mtype = mtype or ""

                    if mtype.startswith("text"):
                        sample = content[: config.sample_size].decode(
                            "utf-8", errors="ignore"
                        )
                    else:
                        sample = ""

                    original = utils.clean_filename(pfile.stem)

                    database.add_post(
                        user_id=user.id,
                        name=name,
                        ext=path.suffix[1:],
                        title=title,
                        original=original,
                        mtype=mtype,
                        size=file_size,
                        sample=sample,
                        file_hash=file_hash,
                    )

                    database.update_user_last_date(user.id)
                except Exception as e:
                    utils.error(e)
                    return error("Failed to save file")

                post_procs.check_storage()

                if mode == "normal":
                    return True, name

                return True, f"post/{name}"

            return error("File is empty")
        except Exception as e:
            utils.error(e)
            return error("Failed to read file")
    else:
        return error("File object has no 'read' attribute")

    return error("Nothing was uploaded")


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
