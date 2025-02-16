from __future__ import annotations

# Standard
import os
from dataclasses import dataclass
from pathlib import Path

# Libraries
from flask import jsonify  # type: ignore

# Modules
import utils
import database
from config import config
from database import File as DbFile
from user_procs import User


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
    sample: str
    show: str
    listed: bool
    listed_str: str
    post_title: str


def make_file(file: DbFile, now: int, with_sample: bool = False) -> File:
    name = file.name
    date = file.date
    size = file.size
    title = file.title
    views = file.views
    original = file.original
    username = file.username
    uploader = file.uploader
    ext = file.ext
    mtype = file.mtype
    listed = file.listed
    ago = utils.time_ago(date, now)
    date_1 = utils.nice_date(date, "date")
    date_2 = utils.nice_date(date, "time")
    date_3 = utils.nice_date(date)
    size_str = utils.get_size(size)
    listed_str = "L: Yes" if listed else "L: No"
    post_title = title or original or name

    if with_sample:
        sample = file.sample
    else:
        sample = ""

    if original:
        if ext:
            original_full = f"{original}{ext}"
        else:
            original_full = original
    else:
        original_full = ""

    show = f"{name} {ext}".strip()
    can_embed = size <= (config.embed_max_size * 1_000_000)

    if ext:
        full = f"{name}.{ext}"
    else:
        full = name

    return File(
        name,
        ext,
        full,
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
        sample,
        show,
        listed,
        listed_str,
        post_title,
    )


def get_files(
    page: int = 1,
    page_size: str = "default",
    query: str = "",
    sort: str = "date",
    max_files: int = 0,
    username: str = "",
    only_listed: bool = False,
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

    for file in database.get_files():
        if only_listed:
            if not file.listed:
                continue

        if username:
            if file.username != username:
                continue

        f = make_file(file, now)

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

    elif sort == "listed":
        files.sort(key=lambda x: x.listed, reverse=True)
    elif sort == "listed_desc":
        files.sort(key=lambda x: x.listed, reverse=False)

    total_size_str = utils.get_size(total_size)
    total_str = f"{total_size_str} ({len(files)} Files)"

    if max_files > 0:
        files = files[:max_files]

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


def get_file(name: str) -> File | None:
    file = database.get_file(name)

    if file:
        now = utils.now()
        return make_file(file, now, True)

    return None


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


def get_next_file(name: str) -> str | None:
    if not name:
        return None

    file = database.get_next_file(name)
    return file.name if file else None


def get_random_file(used_names: list[str]) -> str | None:
    file = database.get_random_file(used_names)
    return file.name if file else None
