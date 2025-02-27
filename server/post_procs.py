from __future__ import annotations

# Standard
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Modules
import utils
import database
import react_procs
from config import config
from database import Post as DbPost
from user_procs import User
from react_procs import Reaction


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
    sample: str
    show: str
    listed: bool
    listed_str: str
    post_title: str
    reactions: list[Reaction]
    num_reactions: int
    views_str: str
    uploader_str: str
    mtype_str: str
    image_embed: bool
    video_embed: bool
    audio_embed: bool
    flash_embed: bool
    text_embed: bool
    markdown_embed: bool


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
    uploader_str = uploader or "Anon"
    mtype_str = mtype or ext or "?"
    num_reactions = post.num_reactions

    if all_data:
        sample = post.sample
        reactions = [react_procs.make_reaction(r, now) for r in post.reactions]
    else:
        sample = ""
        reactions = []

    show = f"{name} {ext}".strip()
    views_str = f"V: {views} | R: {num_reactions}"

    def embed_size(mtype: str) -> bool:
        max_size = int(getattr(config, f"embed_max_size_{mtype}"))

        if max_size <= 0:
            return True

        return size <= (max_size * 1_000_000)

    image_embed = mtype.startswith("image/") and embed_size("image")
    video_embed = mtype.startswith("video/") and embed_size("video")
    audio_embed = mtype.startswith("audio/") and embed_size("audio")

    flash_embed = (
        mtype.startswith("application/") and ("flash" in mtype) and embed_size("flash")
    )

    text_embed = mtype.startswith("text/") and embed_size("text")
    markdown_embed = (mtype == "text/markdown") and embed_size("markdown")

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
        sample,
        show,
        listed,
        listed_str,
        post_title,
        reactions,
        num_reactions,
        views_str,
        uploader_str,
        mtype_str,
        image_embed,
        video_embed,
        audio_embed,
        flash_embed,
        text_embed,
        markdown_embed,
    )


def get_postlist(
    user_id: int | None = None, full_reactions: bool = False
) -> list[Post]:
    now = utils.now()
    posts = database.get_posts(user_id=user_id, full_reactions=full_reactions)
    return [make_post(post, now) for post in posts]


def get_posts(
    page: int = 1,
    page_size: str = "default",
    query: str = "",
    sort: str = "date",
    max_posts: int = 0,
    user_id: int | None = None,
    only_listed: bool = False,
    admin: bool = False,
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
    query = utils.clean_query(query)

    for post in get_postlist(user_id):
        if only_listed:
            if not post.listed:
                continue

        ok = (
            not query
            or (admin and (query in utils.clean_query(post.username)))
            or query in utils.clean_query(post.full)
            or query in utils.clean_query(post.original)
            or query in utils.clean_query(post.title)
            or query in utils.clean_query(post.uploader)
            or query in utils.clean_query(post.date_3)
            or query in utils.clean_query(post.size_str)
            or query in utils.clean_query(post.views_str)
            or query in utils.clean_query(post.mtype)
            or query in utils.clean_query(post.uploader_str)
            or query in utils.clean_query(post.ago)
            or query in utils.clean_query(post.listed_str)
        )

        if not ok:
            continue

        total_size += post.size
        posts.append(post)

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

    elif sort == "mtype":
        posts.sort(key=lambda x: x.mtype, reverse=True)
    elif sort == "mtype_desc":
        posts.sort(key=lambda x: x.mtype, reverse=False)


def get_post(
    post_id: int | None = None,
    name: str | None = None,
    full: bool = False,
    increase: bool = False,
) -> Post | None:
    post = database.get_post(post_id=post_id, name=name)

    if post:
        now = utils.now()

        if increase:
            diff = now - post.view_date

            if diff > config.view_delay:
                increase_post_views(post_id)

        return make_post(post, now, full)

    return None


def increase_post_views(post_id: int | None) -> None:
    if not post_id:
        return

    database.increase_post_views(post_id)


def get_next_post(post_id: int) -> str | None:
    if not post_id:
        return None

    post = database.get_next_post(post_id)
    return post.name if post else None


def get_random_post(used_ids: list[int]) -> str | None:
    post = database.get_random_post(used_ids)
    return post.name if post else None


def delete_posts(ids: list[int]) -> tuple[str, int]:
    if not ids:
        return utils.bad("Post ids were not provided")

    for post_id in ids:
        post = database.get_post(post_id)

        if post:
            do_delete_post(post)

    return utils.ok("Post deleted successfully")


def delete_post(post_id: int, user: User) -> tuple[str, int]:
    if not post_id:
        return utils.bad("Post post_id was not provided")

    if not user.admin:
        if not config.allow_edit:
            return utils.bad("Editing is disabled")

        db_post = database.get_post(post_id)

        if not db_post:
            return utils.bad("Post not found")

        if db_post.username != user.username:
            return utils.bad("You are not the uploader")

    post = database.get_post(post_id)

    if post:
        do_delete_post(post)
        return utils.ok("Post deleted successfully")

    return utils.bad("Post not found")


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

    if not utils.check_dir(str(fd)):
        return

    path = fd / file_name
    file = Path(path)

    if file.exists() and file.is_file():
        file.unlink()


def delete_all_posts() -> tuple[str, int]:
    database.delete_all_posts()
    database.delete_all_reactions()
    delete_all_files()
    return utils.ok("All posts deleted")


def delete_all_files() -> None:
    fd = utils.files_dir()

    if not utils.check_dir(str(fd)):
        return

    for root, _, filenames in os.walk(fd):
        for name in filenames:
            if name.startswith("."):
                continue

            file_path = Path(root) / Path(name)
            file_path.unlink()


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
        post = database.get_post(name=name)

        if post:
            do_delete_post(post)


def edit_post_title(post_id: int, title: str, user: User) -> tuple[str, int]:
    title = title or ""

    if not post_id:
        return utils.bad("Missing values")

    if len(title) > config.max_title_length:
        return utils.bad("Title is too long")

    if not user.admin:
        if not config.allow_edit:
            return utils.bad("Editing is disabled")

        db_post = database.get_post(post_id)

        if not db_post:
            return utils.bad("Post not found")

        if db_post.username != user.username:
            return utils.bad("You are not the uploader")

    database.edit_post_title(post_id, title)
    return utils.ok("Title updated")


def get_latest_post() -> Post | None:
    post = database.get_latest_post()

    if post:
        return make_post(post, utils.now(), False)

    return None


def get_post_update(post_id: int) -> tuple[bool, dict[str, Any]]:
    post = get_post(post_id, full=True, increase=False)

    if post:
        return True, {
            "title": post.title,
            "post_title": post.post_title,
            "uploader": post.uploader,
            "reactions": [r.to_dict() for r in post.reactions],
            "views": post.views,
        }

    return False, {}
