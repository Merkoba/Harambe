from __future__ import annotations

# Standard
import os
import time
import mimetypes
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
import user_procs
from user_procs import User
from config import config


@dataclass
class File:
    name: str
    ext: str
    full: str
    original: str
    original_full: str
    date: int
    date_1: str
    date_2: str
    date_3: str
    ago: str
    size: int
    size_str: str
    title: str
    views: int
    username: str
    uploader: str
    mtype: str
    can_embed: bool
    content: str
    show: str


class UserData:
    def __init__(self, rpm: int) -> None:
        self.timestamps: deque[float] = deque()
        self.rpm = rpm
        self.window = 60

    def increment(self) -> None:
        now = time.time()
        self.timestamps.append(now)

        while self.timestamps and (self.timestamps[0] < (now - self.window)):
            self.timestamps.popleft()

    def blocked(self) -> bool:
        self.increment()
        return len(self.timestamps) > self.rpm


user_data: dict[str, UserData] = {}


def check_user_limit(user: User) -> tuple[bool, str]:
    if user.username not in user_data:
        user_data[user.username] = UserData(user.rpm)

    if user_data[user.username].blocked():
        return False, "Rate limit exceeded"

    return True, "ok"


def check_user_max(user: User, size: int) -> bool:
    megas = int(size / 1000 / 1000)

    if user.max_size > 0:
        if megas > user.max_size:
            return False

    return True


def upload(request: Any, mode: str = "normal", username: str = "") -> tuple[bool, str]:
    def error(s: str) -> tuple[bool, str]:
        return False, f"Error: {s}"

    title = request.form.get("title", "")

    if len(title) > config.max_title_length:
        return error("Title is too long")

    user = None

    if mode == "normal":
        if config.require_captcha:
            c_hash = request.form.get("captcha-hash", "")
            c_text = request.form.get("captcha-text", "")

            check_catpcha = True

            if username:
                check_catpcha = False

            if check_catpcha:
                if config.captcha_cheat and (c_text == config.captcha_cheat):
                    check_catpcha = False

            if check_catpcha:
                if not app.simple_captcha.verify(c_text, c_hash):
                    return error("Failed captcha")
    elif mode == "cli":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if (not username) or (not password):
            return error("Missing username or password")

        if (len(username) > 255) or (len(password) > 255):
            return error("Invalid username or password")

        user = user_procs.check_auth(username, password)

        if not user:
            return error("Invalid username or password")

        u_ok, u_msg = check_user_limit(user)

        if not u_ok:
            return error(u_msg)

    if (not user) and username:
        user = user_procs.get_user(username)

    file = request.files.get("file", None)

    if not file:
        return error("No file")

    if not file.name:
        return error("No file name")

    if len(file.name) > 255:
        return error("File name is too long")

    if hasattr(file, "read"):
        try:
            content = file.read()
            length = len(content)
            toobig = "File is too big"

            if user and user.max_size > 0:
                if not check_user_max(user, length):
                    return error(toobig)
            elif length > config.max_size:
                return error(toobig)

            if content:
                file.seek(0)
                fname = file.filename
                pfile = Path(fname)
                ext = pfile.suffix.lower()
                name = pfile.stem
                u = ulid.new()
                name = u.str[: config.get_file_name_length()]

                if user and user.mark:
                    name = f"{name}_{user.mark}".strip()

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

                    if config.allow_titles:
                        title = utils.clean_title(title)
                    else:
                        title = ""

                    if user:
                        uploader = user.name
                    else:
                        uploader = ""

                    mtype, _ = mimetypes.guess_type(path)

                    database.add_file(
                        name,
                        cext,
                        title,
                        pfile.stem,
                        username,
                        uploader,
                        mtype or "",
                    )
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
    date_1 = utils.nice_date(date, "date")
    date_2 = utils.nice_date(date, "time")
    date_3 = utils.nice_date(date)
    ago = utils.time_ago(date, now)
    size_str = utils.get_size(size)

    if db_file:
        title = db_file.title
        views = db_file.views
        original = db_file.original
        username = db_file.username
        uploader = db_file.uploader
        ext = db_file.ext
        mtype = db_file.mtype
    else:
        title = ""
        views = 0
        original = ""
        username = ""
        uploader = ""
        mtype = ""

        if file.suffix:
            ext = file.suffix[1:]
        else:
            ext = ""

    if original:
        if file.suffix:
            original_full = f"{original}{file.suffix}"
        else:
            original_full = original
    else:
        original_full = ""

    if mtype.startswith("text"):
        with file.open("r") as f:
            content = f.read(config.max_file_content)
    else:
        content = ""

    show = f"{file.stem} {ext}".strip()
    can_embed = size <= config.embed_max_size

    return File(
        file.stem,
        ext,
        file.name,
        original,
        original_full,
        date,
        date_1,
        date_2,
        date_3,
        ago,
        size,
        size_str,
        title,
        views,
        username,
        uploader,
        mtype,
        can_embed,
        content,
        show,
    )


def get_files(
    page: int = 1,
    page_size: str = "default",
    query: str = "",
    sort: str = "date",
    max_files: int = 0,
    username: str = "",
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
        db_file = db_files.get(file.stem, None)

        if username:
            if not db_file:
                continue

            if db_file.username != username:
                continue

        f = make_file(file, db_file, now)

        ok = (
            not query
            or query in f.full.lower()
            or query in f.original.lower()
            or query in f.title.lower()
            or query in f.uploader.lower()
            or query in f.date_3.lower()
            or query in f.size_str.lower()
            or ((query == "anon") and (not f.uploader))
        )

        if not ok:
            continue

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

    elif sort == "title":
        files.sort(key=lambda x: x.title, reverse=True)
    elif sort == "title_desc":
        files.sort(key=lambda x: x.title, reverse=False)

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
        do_delete_file(file)

    return jsonify({"status": "ok", "message": "File deleted successfully"}), 200


def delete_file(file: str, user: User) -> tuple[str, int]:
    if not file:
        return jsonify(
            {"status": "error", "message": "File name was not provided"}
        ), 400

    if not user.admin:
        if not config.allow_edit:
            return jsonify({"status": "error", "message": "Editing is disabled"}), 500

        name = Path(file).stem
        db_file = database.get_file(name)

        if not db_file:
            return jsonify({"status": "error", "message": "File not found"}), 500

        if db_file.username != user.username:
            return jsonify(
                {"status": "error", "message": "You are not the uploader"}
            ), 500

    do_delete_file(file)
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
        database.delete_file(name)


def delete_all_files() -> tuple[str, int]:
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


def edit_title(name: str, title: str, user: User) -> tuple[str, int]:
    title = title or ""

    if not name:
        return jsonify({"status": "error", "message": "Missing values"}), 500

    if len(title) > config.max_title_length:
        return jsonify({"status": "error", "message": "Title is too long"}), 500

    if not user.admin:
        if not config.allow_edit:
            return jsonify({"status": "error", "message": "Editing is disabled"}), 500

        db_file = database.get_file(name)

        if not db_file:
            return jsonify({"status": "error", "message": "File not found"}), 500

        if db_file.username != user.username:
            return jsonify(
                {"status": "error", "message": "You are not the uploader"}
            ), 500

    database.edit_title(name, title)
    return jsonify({"status": "ok", "message": "Title updated"}), 200
