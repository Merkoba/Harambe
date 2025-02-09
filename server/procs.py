from __future__ import annotations

# Standard
import os
import time
from typing import Any
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from collections import deque

# Libraries
from flask import jsonify  # type: ignore
import ulid  # type: ignore

# Modules
import app
import utils
from config import config, Key


@dataclass
class Message:
    message: str
    mode: str
    data: str = ""


@dataclass
class File:
    name: str
    date: datetime
    nice_date: str
    ago: str
    size: float
    size_str: str


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


def error(s: str) -> Message:
    return Message(f"Error: {s}", "error")


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


def upload(request: Any, mode: str = "normal") -> Message:
    file = request.files.get("file", None)

    if not file:
        return error("No file")

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
                except Exception:
                    return error("Failed to save file")

                check_storage()
                fpath = f"file/{new_name}"

                if mode == "normal":
                    mb = round(length / 1_000_000, 2)
                    m = f'Uploaded: <a class="link" href="/{fpath}">{new_name}</a> ({mb} mb)'
                    return Message(m, "upload", fpath)

                return Message(fpath, "key_upload")

            return error("File is empty")
        except Exception as e:
            utils.error(e)
            return error("Failed to read file")
    else:
        return error("File object has no 'read' attribute")

    return error("Nothing was uploaded")


def get_files(
    page: int = 1, page_size: str = "default"
) -> tuple[list[File], str, bool]:
    psize = 0

    if page_size == "default":
        psize = config.admin_page_size
    elif page_size == "all":
        pass  # Don't slice later
    else:
        psize = int(page_size)

    all_files = list(utils.files_dir().glob("*"))

    files = []
    total_size = 0
    now = utils.now()

    for f in all_files:
        if f.name.startswith("."):
            continue

        date = datetime.fromtimestamp(f.stat().st_mtime)
        size = int(f.stat().st_size)
        total_size += size
        nice_date = utils.nice_date(date)
        ago = utils.time_ago(date, now)
        size_str = utils.get_size(size)
        files.append(File(f.name, date, nice_date, ago, size, size_str))

    total_size_str = utils.get_size(total_size)
    total_str = f"{total_size_str} ({len(files)} Files)"
    files.sort(key=lambda x: x.date, reverse=True)

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

    if file.exists():
        file.unlink()


def delete_all() -> tuple[str, int]:
    try:
        do_delete_all()

        return jsonify(
            {"status": "ok", "message": "All files deleted successfully"}
        ), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def do_delete_all() -> None:
    files = utils.files_dir().glob("*")

    for file in files:
        if file.name.startswith("."):
            continue

        do_delete_file(file.name)


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
