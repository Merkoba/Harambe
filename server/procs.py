from __future__ import annotations

# Standard
import os
import time
from typing import Any
from pathlib import Path
from dataclasses import dataclass
from collections import deque

# Libraries
from flask import jsonify  # type: ignore
import ulid  # type: ignore

# Modules
import app
import utils
import log
from config import config, Key
from database import database
from database import File as DbFile


@dataclass
class File:
    id: str
    name: str
    date: int
    nice_date: str
    ago: str
    size: int
    size_str: str
    comment: str


class KeyData:
    def __init__(self, limit: int) -> None:
        self.timestamps: deque[float] = deque()
        self.limit = limit
        self.window = 60  # Rate limit per minute

    def increment(self) -> None:
        now = time.time()
        self.timestamps.append(now)

        while self.timestamps and (self.timestamps[0] < (now - self.window)):
            self.timestamps.popleft()

    def blocked(self) -> bool:
        self.increment()
        return len(self.timestamps) > self.limit


key_data: dict[str, KeyData] = {}


def check_key(name: str) -> tuple[bool, str, Key | None]:
    if not name:
        return False, "Key is required", None

    key = None

    for k in config.keys:
        if name == k.name:
            key = k
            break

    if not key:
        return False, "Invalid key", None

    if name not in key_data:
        key_data[name] = KeyData(key.limit)

    d = key_data[name]

    if d.blocked():
        return False, "Rate limit exceeded", key

    return True, "ok", key


def upload(request: Any, mode: str = "normal") -> tuple[bool, str]:
    def error(s: str) -> tuple[bool, str]:
        return False, f"Error: {s}"

    file = request.files.get("file", None)

    if not file:
        return error("No file")

    comment = request.form.get("comment", "")

    if len(comment) > config.max_comment_length:
        return error("Comment is too long")

    key = request.form.get("key", "")
    used_key = None

    if mode == "normal":
        c_hash = request.form.get("captcha-hash", "")
        c_text = request.form.get("captcha-text", "")

        if config.require_key:
            k_ok, k_msg, used_key = check_key(key)

            if not k_ok:
                return error(k_msg)

        if config.require_captcha:
            check_catpcha = True

            if config.captcha_cheat and (c_text == config.captcha_cheat):
                check_catpcha = False

            if check_catpcha:
                if not app.simple_captcha.verify(c_text, c_hash):
                    return error("Failed captcha")
    elif mode == "cli":
        k_ok, k_msg, used_key = check_key(key)

        if not k_ok:
            return error(k_msg)

    if hasattr(file, "read"):
        try:
            content = file.read()
            length = len(content)

            if length > config.get_max_file_size():
                return error("File is too big")

            if content:
                file.seek(0)
                fname = file.filename
                pfile = Path(fname)
                ext = pfile.suffix.lower()
                name = pfile.stem
                u = ulid.new()
                name = u.str[: config.get_file_name_length()]

                if used_key and used_key.id:
                    k_id = used_key.id.strip()
                    name = f"{name}_{k_id}"

                if not config.uppercase_ids:
                    name = name.lower()

                if ext:
                    new_name = f"{name}{ext}"
                else:
                    new_name = name

                path = utils.files_dir() / new_name

                try:
                    file.save(path)
                    comment = utils.clean_comment(comment)
                    db_file = database.add_file(new_name, length, comment)
                except Exception as e:
                    utils.error(e)
                    return error("Failed to save file")

                check_storage()

                if mode == "normal":
                    return True, db_file.id

                return True, db_file.name

            return error("File is empty")
        except Exception as e:
            utils.error(e)
            return error("Failed to read file")
    else:
        return error("File object has no 'read' attribute")

    return error("Nothing was uploaded")


def make_file(file: DbFile, now: int) -> File:
    date = file.date
    size = file.size
    nice_date = utils.nice_date(date)
    ago = utils.time_ago(date, now)
    size_str = utils.get_size(size)
    comment = file.comment

    return File(file.id, file.name, date, nice_date, ago, size, size_str, comment)


def get_files(
    page: int = 1,
    page_size: str = "default",
    query: str = "",
    sort: str = "date",
    max_files: int = 0,
) -> tuple[list[File], str, bool]:
    psize = 0

    if page_size == "default":
        psize = config.admin_page_size
    elif page_size == "all":
        pass  # Don't slice later
    else:
        psize = int(page_size)

    files = []
    total_size = 0
    now = utils.now()
    query = query.lower()

    for file in database.files:
        if query and (query not in file.name.lower()):
            continue

        f = make_file(file, now)
        total_size += f.size
        files.append(f)

    if sort == "date":
        files.sort(key=lambda x: x.date, reverse=True)
    elif sort == "date_desc":
        files.sort(key=lambda x: x.date, reverse=False)
    elif sort == "size":
        files.sort(key=lambda x: x.size, reverse=True)
    elif sort == "size_desc":
        files.sort(key=lambda x: x.size, reverse=False)

    if max_files > 0:
        files = files[:max_files]

    total_size_str = utils.get_size(total_size)
    total_str = f"{total_size_str} ({len(files)} Files)"

    if psize > 0:
        start_index = (page - 1) * psize
        end_index = start_index + psize
        has_next_page = end_index < len(files)
        files = files[start_index:end_index]
    else:
        has_next_page = False

    return files, total_str, has_next_page


def delete_files(files: list[str]) -> tuple[str, int]:
    if not files:
        return jsonify(
            {"status": "error", "message": "File names were not provided"}
        ), 400

    for file in files:
        if file.startswith("."):
            continue

        try:
            do_delete_file(file)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "ok", "message": "File deleted successfully"}), 200


# Be extra careful with this function
def do_delete_file(name: str) -> None:
    if not config.allow_delete:
        return

    if not name:
        return

    if not utils.valid_file_name(name):
        return

    fd = utils.files_dir()
    fds = str(fd)

    if not fds:
        return

    if fds == "/":
        return

    if fds == ".":
        return

    if (fds == "~") or (fds == "~/"):
        return

    if fds == "/home":
        return

    path = fd / name
    file = Path(path)

    if file.exists() and file.is_file():
        file.unlink()
        database.remove_file(name)


def delete_all() -> tuple[str, int]:
    try:
        files = utils.files_dir().glob("*")

        for file in files:
            if file.name.startswith("."):
                continue

            do_delete_file(file.name)

        return jsonify(
            {"status": "ok", "message": "All files deleted successfully"}
        ), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Remove old files if limits are exceeded
def check_storage() -> None:
    directory = utils.files_dir()
    max_files = config.max_files
    max_storage = config.get_max_storage()

    total_files = 0
    total_size = 0
    files = []

    for root, _, filenames in os.walk(directory):
        for name in filenames:
            file_path = Path(root) / Path(name)
            file_size = file_path.stat().st_size
            files.append((file_path, file_size))
            total_files += 1
            total_size += file_size

    files.sort(key=lambda x: x[0])

    def exceeds() -> bool:
        return (total_files > max_files) or (total_size > max_storage)

    while exceeds():
        oldest_file = files.pop(0)
        oldest_file[0].unlink()
        total_files -= 1
        total_size -= oldest_file[1]


def get_image_name() -> str:
    if Path("static/img/banner.jpg").exists():
        return "banner.jpg"

    if Path("static/img/banner.png").exists():
        return "banner.png"

    if Path("static/img/banner.gif").exists():
        return "banner.gif"

    return "cat.jpg"


def get_file(id_: str) -> File | None:
    file = database.get_file(id_)
    log.info(id_)

    if not file:
        return None

    log.info("file111", file.id)
    return make_file(file, utils.now())
