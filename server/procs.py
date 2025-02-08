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
from config import config


@dataclass
class Message:
    message: str
    mode: str
    data: str = ""


class KeyData:
    def __init__(self) -> None:
        self.timestamps: deque[float] = deque()
        self.limit = config.key_limit
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
    return Message(f"🔴 Error: {s}", "error")


def check_key(key: str) -> tuple[bool, str]:
    if not key:
        return False, "Key is required"

    if key not in config.keys:
        return False, "Invalid key"

    if key not in key_data:
        key_data[key] = KeyData()

    d = key_data[key]

    if d.blocked():
        return False, "Rate limit exceeded"

    return True, "ok"


def upload(request: Any, mode: str = "normal") -> Message:
    file = request.files.get("file", None)

    if not file:
        return error("No file")

    key = request.form.get("key", "")

    if mode == "normal":
        c_hash = request.form.get("captcha-hash", "")
        c_text = request.form.get("captcha-text", "")

        if config.require_key:
            k_ok, k_msg = check_key(key)

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
        k_ok, k_msg = check_key(key)

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
                ext = pfile.suffix
                name = pfile.stem
                u = ulid.new()

                if config.extra_unique_ids:
                    name = u.str
                else:
                    name = u.timestamp().str

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
                    m = f'🟢 Uploaded: <a class="link" href="/{fpath}">{new_name}</a> ({mb} mb)'
                    return Message(m, "upload", fpath)

                return Message(fpath, "key_upload")

            return error("File is empty")
        except Exception as e:
            utils.error(e)
            return error("Failed to read file")
    else:
        return error("File object has no 'read' attribute")

    return error("Nothing was uploaded")


def time_ago(date: float) -> str:
    return utils.time_ago(date, utils.now())


def dashboard(page: int = 1) -> tuple[list[dict[str, Any]], str, bool]:
    files = list(utils.files_dir().glob("*"))
    files = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)

    page_size = config.admin_page_size
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    has_next_page = end_index < len(files)
    files = files[start_index:end_index]

    total_size = 0
    file_list = []

    for f in files:
        if f.name.startswith("."):
            continue

        size = f.stat().st_size
        total_size += size

        file_list.append(
            {
                "name": f.name,
                "size": utils.get_size(size),
                "ago": time_ago(f.stat().st_mtime),
            }
        )

    gigas = round(total_size / 1_000_000_000, 2)
    megas = round(total_size / 1_000_000, 2)

    if gigas >= 1:
        total_str = f"{gigas} GB"
    else:
        total_str = f"{megas} MB"

    total_str = f"{total_str} | {len(file_list)} Files"
    return file_list, total_str, has_next_page


def delete_file(name: str) -> tuple[str, int]:
    if not name:
        return jsonify({"status": "error", "message": "Filename is required"}), 400

    if name.startswith("."):
        return jsonify({"status": "error", "message": "Invalid filename"}), 400

    try:
        do_delete_file(name)
        return jsonify({"status": "ok", "message": "File deleted successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def do_delete_file(name: str) -> None:
    path = utils.files_dir() / name
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

        file.unlink()


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
