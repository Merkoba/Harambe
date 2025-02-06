from __future__ import annotations

# Standard
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
import config


@dataclass
class Message:
    message: str
    mode: str
    data: str = ""


class KeyData:
    def __init__(self):
        self.timestamps = deque()
        self.limit = config.key_limit
        self.window = 60  # Rate limit per minute

    def increment(self):
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


def upload(request: Any, mode: str = "normal") -> Message:
    file = request.files.get("file", None)

    if not file:
        return error("No file")

    if mode == "normal":
        c_hash = request.form.get("captcha-hash", "")
        c_text = request.form.get("captcha-text", "")
        code = request.form.get("code", "")

        if config.codes and (code not in config.codes):
            return error("Invalid code")

        if config.captcha_enabled:
            check_catpcha = True

            if config.captcha_cheat and (c_text == config.captcha_cheat):
                check_catpcha = False

            if check_catpcha:
                if not app.simple_captcha.verify(c_text, c_hash):
                    return error("Failed captcha")
    elif mode == "user":
        key = request.form.get("key", "")

        if not key:
            return error("Key is required")

        if key not in config.keys:
            return error("Invalid key")

        if key not in key_data:
            key_data[key] = KeyData()

        d = key_data[key]

        if d.blocked():
            return error("Rate limit exceeded")

    if hasattr(file, "read"):
        try:
            content = file.read()
            length = len(content)

            if length > config.max_file_size:
                return error("File is too big")

            if content:
                file.seek(0)
                fname = file.filename
                pfile = Path(fname)
                ext = pfile.suffix
                name = pfile.stem
                name = ulid.new().timestamp().str

                if ext:
                    new_name = f"{name}{ext}"
                else:
                    new_name = name

                path = utils.files_dir() / new_name

                try:
                    file.save(path)
                except Exception:
                    return error("Failed to save file")

                fpath = f"file/{new_name}"

                if mode == "normal":
                    mb = round(length / 1_000_000, 2)
                    m = f'Uploaded: <a class="link" href="/{fpath}">{new_name}</a> ({mb} mb)'
                    return Message(m, "upload", fpath)
                elif mode == "user":
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


def get_files() -> list[dict[str, Any]]:
    files = list(utils.files_dir().glob("*"))
    files = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
    files = files[: config.admin_max_files]

    return [
        {
            "name": f.name,
            "size": utils.get_size(f.stat().st_size),
            "ago": time_ago(f.stat().st_mtime),
        }
        for f in files
        if not f.name.startswith(".")
    ]


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
