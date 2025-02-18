from __future__ import annotations

# Standard
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

# Libraries
from flask import jsonify  # type: ignore

# Modules
import utils
import database
from config import config
from database import Post as DbPost
from database import Reaction as DbReaction
from user_procs import User


@dataclass
class Reaction:
    post: str
    user: str
    uname: str
    value: str
    mode: str
    date: int
    ago: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Post:
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
    reactions: list[Reaction]


def make_reaction(reaction: DbReaction, now: int) -> Reaction:
    ago = utils.time_ago(reaction.date, now)

    return Reaction(
        reaction.post,
        reaction.user,
        reaction.uname,
        reaction.value,
        reaction.mode,
        reaction.date,
        ago,
    )


def make_post(post: DbPost, now: int, all_data: bool = False) -> Post:
    name = post.name
    ext = post.ext
    full = post.full()
    title = post.title
    date = post.date
    size = post.size
    views = post.views
    username = post.username
    uploader = post.uploader
    mtype = post.mtype
    listed = post.listed
    original = post.original
    original_full = post.original_full()
    ago = utils.time_ago(date, now)
    date_1 = utils.nice_date(date, "date")
    date_2 = utils.nice_date(date, "time")
    date_3 = utils.nice_date(date)
    size_str = utils.get_size(size)
    listed_str = "L: Yes" if listed else "L: No"
    post_title = title or original or name

    if all_data:
        sample = post.sample

        try:
            reactions = [make_reaction(r, now) for r in database.get_reactions(name)]
        except Exception as e:
            utils.error(e)
            reactions = []
    else:
        sample = ""
        reactions = []

    show = f"{name} {ext}".strip()
    can_embed = size <= (config.embed_max_size * 1_000_000)

    return Post(
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
        reactions,
    )


def get_posts(
    page: int = 1,
    page_size: str = "default",
    query: str = "",
    sort: str = "date",
    max_posts: int = 0,
    username: str = "",
    only_listed: bool = False,
) -> tuple[list[Post], str, bool]:
    psize = 0

    if page_size == "default":
        psize = config.admin_page_size
    elif page_size == "all":
        pass  # Don't slice later
    else:
        psize = int(page_size)

    posts = []
    total_size = 0
    now = utils.now()
    query = query.lower()

    for post in database.get_posts():
        if only_listed:
            if not post.listed:
                continue

        if username:
            if post.username != username:
                continue

        f = make_post(post, now, False)

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
        posts.append(f)

    total_size_str = utils.get_size(total_size)
    total_str = f"{total_size_str} ({len(posts)} Posts)"
    sort_posts(posts, sort)

    if max_posts > 0:
        posts = posts[:max_posts]

    if psize > 0:
        start_index = (page - 1) * psize
        end_index = start_index + psize
        has_next_page = end_index < len(posts)
        posts = posts[start_index:end_index]
    else:
        has_next_page = False

    return posts, total_str, has_next_page


def sort_posts(posts: list[Post], sort: str) -> None:
    if sort == "date":
        posts.sort(key=lambda x: x.date, reverse=True)
    elif sort == "date_desc":
        posts.sort(key=lambda x: x.date, reverse=False)

    elif sort == "size":
        posts.sort(key=lambda x: x.size, reverse=True)
    elif sort == "size_desc":
        posts.sort(key=lambda x: x.size, reverse=False)

    elif sort == "views":
        posts.sort(key=lambda x: x.views, reverse=True)
    elif sort == "views_desc":
        posts.sort(key=lambda x: x.views, reverse=False)

    elif sort == "title":
        posts.sort(key=lambda x: x.title, reverse=True)
    elif sort == "title_desc":
        posts.sort(key=lambda x: x.title, reverse=False)

    elif sort == "name":
        posts.sort(key=lambda x: x.name, reverse=True)
    elif sort == "name_desc":
        posts.sort(key=lambda x: x.name, reverse=False)

    elif sort == "listed":
        posts.sort(key=lambda x: x.listed, reverse=True)
    elif sort == "listed_desc":
        posts.sort(key=lambda x: x.listed, reverse=False)

    elif sort == "uploader":
        posts.sort(key=lambda x: x.uploader, reverse=True)
    elif sort == "uploader_desc":
        posts.sort(key=lambda x: x.uploader, reverse=False)


def get_post(name: str, full: bool = False, increase: bool = False) -> Post | None:
    post = database.get_post(name)

    if post:
        now = utils.now()

        if increase:
            diff = now - post.view_date

            if diff > config.view_delay:
                increase_post_views(name)

        return make_post(post, now, full)

    return None


def increase_post_views(name: str) -> None:
    database.increase_post_views(name)


def get_next_post(name: str) -> str | None:
    if not name:
        return None

    post = database.get_next_post(name)
    return post.name if post else None


def get_random_post(used_names: list[str]) -> str | None:
    post = database.get_random_post(used_names)
    return post.name if post else None


def delete_posts(names: list[str]) -> tuple[str, int]:
    if not names:
        return jsonify(
            {"status": "error", "message": "Post names were not provided"}
        ), 400

    for name in names:
        post = database.get_post(name)

        if post:
            do_delete_post(post)

    return jsonify({"status": "ok", "message": "Post deleted successfully"}), 200


def delete_post(name: str, user: User) -> tuple[str, int]:
    if not name:
        return jsonify(
            {"status": "error", "message": "Post name was not provided"}
        ), 400

    if not user.admin:
        if not config.allow_edit:
            return jsonify({"status": "error", "message": "Editing is disabled"}), 500

        db_post = database.get_post(name)

        if not db_post:
            return jsonify({"status": "error", "message": "Post not found"}), 500

        if db_post.username != user.username:
            return jsonify(
                {"status": "error", "message": "You are not the uploader"}
            ), 500

    post = database.get_post(name)

    if post:
        do_delete_post(post)
        return jsonify({"status": "ok", "message": "Post deleted successfully"}), 200

    return jsonify({"status": "error", "message": "Post not found"}), 500


# Be extra careful with this function!
def do_delete_post(post: DbPost) -> None:
    if not config.allow_delete:
        return

    if not post:
        return

    database.delete_post(post.name)
    file_name = post.full()

    if file_name.startswith("."):
        return

    if not utils.valid_file_name(file_name):
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

    path = fd / file_name
    file = Path(path)

    if file.exists() and file.is_file():
        file.unlink()


def delete_all_posts() -> tuple[str, int]:
    for post in database.get_posts():
        do_delete_post(post)

    return jsonify({"status": "ok", "message": "All posts deleted"}), 200


# Remove old files if limits are exceeded
def check_storage() -> None:
    directory = utils.files_dir()
    max_posts = config.max_posts
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
        return (total_files > max_posts) or (total_size > max_storage)

    while exceeds():
        oldest_file = files.pop(0)
        total_files -= 1
        total_size -= oldest_file[1]
        name = oldest_file[0].name
        post = database.get_post(name)

        if post:
            do_delete_post(post)


def edit_post_title(name: str, title: str, user: User) -> tuple[str, int]:
    title = title or ""

    if not name:
        return jsonify({"status": "error", "message": "Missing values"}), 500

    if len(title) > config.max_title_length:
        return jsonify({"status": "error", "message": "Title is too long"}), 500

    if not user.admin:
        if not config.allow_edit:
            return jsonify({"status": "error", "message": "Editing is disabled"}), 500

        db_post = database.get_post(name)

        if not db_post:
            return jsonify({"status": "error", "message": "Post not found"}), 500

        if db_post.username != user.username:
            return jsonify(
                {"status": "error", "message": "You are not the uploader"}
            ), 500

    database.edit_post_title(name, title)
    return jsonify({"status": "ok", "message": "Title updated"}), 200


def react(name: str, text: str, user: User, mode: str) -> tuple[str, int]:
    if not user:
        return jsonify({"status": "error", "message": "You are not logged in"}), 500

    text = text.strip()

    if not name:
        return jsonify({"status": "error", "message": "Missing values"}), 500

    if not text:
        return jsonify({"status": "error", "message": "Missing values"}), 500

    if mode not in ["character", "icon"]:
        return jsonify({"status": "error", "message": "Invalid mode"}), 500

    if len(text) > 100:
        return jsonify({"status": "error", "message": "Reaction is too long"}), 500

    if mode == "character":
        if len(text) > config.character_reaction_length:
            return jsonify({"status": "error", "message": "Invalid reaction"}), 500
    elif mode == "icon":
        if text not in utils.ICONS:
            return jsonify({"status": "error", "message": "Invalid reaction"}), 500

    if database.get_reaction_count(name, user.username) >= config.max_user_reactions:
        return jsonify(
            {"status": "error", "message": "You can't add more reactions"}
        ), 500

    dbr = database.add_reaction(name, user.username, user.name, text, mode)

    if dbr:
        reaction = make_reaction(dbr, utils.now())
        return jsonify({"status": "ok", "reaction": reaction}), 200

    return jsonify({"status": "error", "message": "Reaction failed"}), 500


def get_latest_post() -> Post | None:
    post = database.get_latest_post()

    if post:
        return make_post(post, utils.now(), False)

    return None


def get_post_update(name: str) -> tuple[bool, dict[str, Any]]:
    post = get_post(name, full=True, increase=False)

    if post:
        return True, {
            "title": post.title,
            "post_title": post.post_title,
            "uploader": post.uploader,
            "reactions": [r.to_dict() for r in post.reactions],
            "views": post.views,
        }

    return False, {}
