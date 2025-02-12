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
import database
from database import File as DbFile
from config import config, Key


@dataclass
class File:
    name: str
    ext: str
    full: str
    original: str
    date: int
    nice_date: str
    ago: str
    size: int
    size_str: str
    comment: str = ""
    views: int = 0


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

    if len(name) > 100:
        return False, "Key is too long", None

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


def check_key_max(key: Key, size: int) -> bool:
    megas = int(size / 1000 / 1000)

    if key.max > 0:
        if megas > key.max:
            return False

    return True


def upload(request: Any, mode: str = "normal") -> tuple[bool, str]:
    def error(s: str) -> tuple[bool, str]:
        return False, f"Error: {s}"

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

    file = request.files.get("file", None)

    if not file:
        return error("No file")

    if hasattr(file, "read"):
        try:
            content = file.read()
            length = len(content)
            toobig = "File is too big"

            if used_key and used_key.max > 0:
                if not check_key_max(used_key, length):
                    return error(toobig)
            elif length > config.get_max_file_size():
                return error(toobig)

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
                    full_name = f"{name}{ext}"
                    cext = ext[1:]
                else:
                    full_name = name
                    cext = ""

                path = utils.files_dir() / full_name

                try:
                    file.save(path)

                    if config.allow_comments:
                        comment = utils.clean_comment(comment)
                    else:
                        comment = ""

                    database.add_file(name, cext, comment, fname)

                except Exception as e:
                    utils.error(e)
                    return error("Failed to save file")

                check_storage()

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


def make_file(file: Path, db_file: DbFile | None, now: int) -> File:
    if db_file:
        date = db_file.date
    else:
        date = int(file.stat().st_mtime)

    size = int(file.stat().st_size)
    nice_date = utils.nice_date(date)
    ago = utils.time_ago(date, now)
    size_str = utils.get_size(size)

    if db_file:
        comment = db_file.comment
        views = db_file.views
        original = db_file.original
    else:
        comment = ""
        views = 0
        original = ""

    return File(
        file.stem,
        file.suffix,
        file.name,
        original,
        date,
        nice_date,
        ago,
        size,
        size_str,
        comment,
        views,
    )


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
    all_files = list(utils.files_dir().glob("*"))
    db_files = database.get_files()

    for file in all_files:
        if query and (query not in file.name.lower()):
            continue

        db_file = db_files.get(file.stem, None)
        f = make_file(file, db_file, now)
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
    elif sort == "views":
        files.sort(key=lambda x: x.views, reverse=True)
    elif sort == "views_desc":
        files.sort(key=lambda x: x.views, reverse=False)
    elif sort == "comment":
        files.sort(key=lambda x: x.comment, reverse=True)
    elif sort == "comment_desc":
        files.sort(key=lambda x: x.comment, reverse=False)
    elif sort == "name":
        files.sort(key=lambda x: x.name, reverse=True)
    elif sort == "name_desc":
        files.sort(key=lambda x: x.name, reverse=False)

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
        total_files -= 1
        total_size -= oldest_file[1]
        do_delete_file(oldest_file[0].name)


def get_image_name() -> str:
    if Path("static/img/banner.jpg").exists():
        return "banner.jpg"

    if Path("static/img/banner.png").exists():
        return "banner.png"

    if Path("static/img/banner.gif").exists():
        return "banner.gif"

    return "cat.jpg"


def get_file(name: str) -> File | None:
    all_files = list(utils.files_dir().glob("*"))

    for file in all_files:
        if file.stem == name:
            db_file = database.get_file(name)

            if db_file:
                database.increase_views(name)

            return make_file(file, db_file, utils.now())

    return None


def increase_view(name: str) -> None:
    database.increase_views(Path(name).stem)
