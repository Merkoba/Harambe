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
    id: int
    user_id: int
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
    show: str
    listed: bool
    listed_str: str
    post_title: str
    reactions: list[Reaction]
    num_reactions: int
    uploader_str: str
    mtype_str: str
    image_embed: bool
    video_embed: bool
    audio_embed: bool
    flash_embed: bool
    markdown_embed: bool
    zip_embed: bool
    last_reaction: str
    file_hash: str
    text: str
    privacy: str
    privacy_str: str
    youtube_id: str
    is_url: bool
    description: str
    value: str

    def is_image(self) -> bool:
        return self.mtype.startswith("image/")

    def is_video(self) -> bool:
        return self.mtype.startswith("video/")

    def is_audio(self) -> bool:
        return self.mtype.startswith("audio/")

    def is_flash(self) -> bool:
        return self.mtype.startswith("application/") and ("flash" in self.mtype)

    def is_text(self) -> bool:
        return (self.mtype.startswith("text/") and ("markdown" not in self.mtype)) or (
            self.mtype == "application/json"
        )

    def is_markdown(self) -> bool:
        return self.mtype.startswith("text/") and ("markdown" in self.mtype)

    def is_zip(self) -> bool:
        return self.mtype.startswith("application/") and ("zip" in self.mtype)


def get_full_name(dbpost: DbPost) -> str:
    if dbpost.ext:
        return f"{dbpost.name}.{dbpost.ext}"

    return dbpost.name


def get_original_name(original: str, dbpost: DbPost) -> str:
    full = utils.clean_filename(original).lower()

    if dbpost.ext:
        full = f"{full}.{dbpost.ext}"

    return full


def make_post(post: DbPost, now: int, all_data: bool = False) -> Post:
    name = post.name
    ext = post.ext
    full = get_full_name(post)
    title = post.title
    date = post.date
    size = post.size
    views = post.views
    mtype = post.mtype
    username = post.author.username if post.author else "Anon"
    uploader = post.author.name if post.author else "Anon"
    lister = post.author.lister if post.author else False
    listed = (post.privacy == "public") and lister
    otl = config.original_title_length
    original = post.original or post.title[:otl].strip() or post.name
    original_full = get_original_name(original, post)
    ago = utils.time_ago(date, now)
    date_1 = utils.nice_date(date, "date")
    date_2 = utils.nice_date(date, "time")
    date_3 = utils.nice_date(date)
    size_str = utils.get_size(size)
    listed_str = "Yes" if listed else "No"
    post_title = title or original or name
    uploader_str = uploader or "Anon"
    mtype_str = mtype or ext or "?"
    num_reactions = post.num_reactions
    privacy = post.privacy
    privacy_str = "Public" if privacy == "public" else "Private"
    lister_str = "Lister" if lister else "Not Lister"
    privacy_str += f" | {lister_str}"
    description = post.description
    value = post.value

    if post.reactions:
        last_reaction = post.reactions[-1].value
    else:
        last_reaction = ""

    if all_data:
        reactions = [react_procs.make_reaction(r, now) for r in post.reactions]
        reactions.sort(key=lambda x: x.date, reverse=False)
    else:
        reactions = []

    show = f"{name} {ext}".strip()

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

    if mtype.startswith("text/"):
        markdown_embed = ("markdown" in mtype) and embed_size("markdown")
    else:
        markdown_embed = False

    zip_embed = mtype.startswith("application/") and ("zip" in mtype)
    file_hash = post.file_hash
    text = ""

    if all_data:
        fname = f"{name}.txt"
        text_file = Path(utils.files_dir() / fname)

        if not text_file.exists():
            text_file = Path(utils.samples_dir() / fname)

        if text_file.exists():
            text = text_file.open("r").read()

    youtube_id = ""
    is_url = False

    if text:
        is_url = utils.is_url(text)

        if is_url:
            yt_info = utils.get_youtube_id(text)

            if yt_info and (yt_info[0] == "video"):
                youtube_id = yt_info[1]

    return Post(
        post.id,
        post.user,
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
        show,
        listed,
        listed_str,
        post_title,
        reactions,
        num_reactions,
        uploader_str,
        mtype_str,
        image_embed,
        video_embed,
        audio_embed,
        flash_embed,
        markdown_embed,
        zip_embed,
        last_reaction,
        file_hash,
        text,
        privacy,
        privacy_str,
        youtube_id,
        is_url,
        description,
        value,
    )


def get_postlist(
    user_id: int | None = None, full_reactions: bool = False, only_public: bool = False
) -> list[Post]:
    now = utils.now()

    posts = database.get_posts(
        user_id=user_id, full_reactions=full_reactions, only_public=only_public
    )

    return [make_post(post, now) for post in posts]


def get_posts(
    page: int = 1,
    page_size: str = "default",
    query: str = "",
    sort: str = "date_asc",
    max_posts: int = 0,
    user_id: int | None = None,
    only_listed: bool = False,
    media_type: str | None = None,
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
    query = utils.decode(query)
    query = utils.clean_query(query)

    for post in get_postlist(user_id, only_public=only_listed):
        if only_listed:
            if not post.listed:
                continue

        props = [
            "username",
            "full",
            "original",
            "title",
            "uploader",
            "date_3",
            "size_str",
            "mtype",
            "uploader_str",
            "ago",
            "listed_str",
            "privacy_str",
            "description",
            "value",
        ]

        if not utils.do_query(post, query, props):
            continue

        if media_type is not None:
            if media_type == "image":
                if not post.is_image():
                    continue
            elif media_type == "video":
                if not post.is_video():
                    continue
            elif media_type == "audio":
                if not post.is_audio():
                    continue
            elif media_type == "flash":
                if not post.is_flash():
                    continue
            elif media_type == "text":
                if not post.is_text():
                    continue
            elif media_type == "markdown":
                if not post.is_markdown():
                    continue
            elif media_type == "zip":
                if not post.is_zip():
                    continue

        total_size += post.size
        posts.append(post)

    total_size_str = utils.get_size(total_size)
    total_str = f"{total_size_str} ({len(posts)})"
    utils.do_sort(posts, sort, ["date"])

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


def get_post(
    post_id: int | None = None,
    name: str | None = None,
    full: bool = False,
    increase: bool = False,
    full_reactions: bool = False,
) -> Post | None:
    if (not post_id) and (not name):
        return None

    posts = database.get_posts(
        post_id=post_id, name=name, full_reactions=full_reactions, increase=increase
    )

    post = posts[0] if posts else None

    if post:
        return make_post(post, utils.now(), full)

    return None


def get_next_post(name: str) -> Post | None:
    if not name:
        return None

    db_post = database.get_next_post(name)

    if db_post:
        return make_post(db_post, utils.now())

    return None


def get_random_post(used_ids: list[int]) -> Post | None:
    db_post = database.get_random_post(used_ids)

    if db_post:
        return make_post(db_post, utils.now())

    return None


def delete_posts(ids: list[int]) -> tuple[str, int]:
    if not ids:
        return utils.bad("Post ids were not provided")

    for post_id in ids:
        post = get_post(post_id)

        if post:
            do_delete_post(post)

    return utils.ok("Post deleted successfully")


def delete_post(post_id: int, user: User) -> tuple[str, int]:
    if not post_id:
        return utils.bad("Post id was not provided")

    if not user.admin:
        if not config.allow_edit:
            return utils.bad("Editing is disabled")

        post = get_post(post_id)

        if not post:
            return utils.bad("Post not found")

        if post.username != user.username:
            return utils.bad("You are not the uploader")

    post = get_post(post_id)

    if post:
        do_delete_post(post)
        return utils.ok("Post deleted successfully")

    return utils.bad("Post not found")


def do_delete_post(post: Post) -> None:
    if not config.allow_delete:
        return

    if not post:
        return

    database.delete_post(post.id)
    file_name = post.full
    try_delete_file(file_name)
    delete_sample(post.name)


def delete_sample(name: str) -> None:
    for file in utils.samples_dir().iterdir():
        if file.stem == name:
            try_delete_file(file.name, "sample")
            break


# Be extra careful with this function!
def try_delete_file(file_name: str, kind: str = "file") -> None:
    if not file_name:
        return

    if file_name.startswith("."):
        return

    if not utils.valid_file_name(file_name):
        return

    if kind == "file":
        rootdir = utils.files_dir()
    elif kind == "sample":
        rootdir = utils.samples_dir()
    else:
        return

    if not utils.check_dir(str(rootdir)):
        return

    path = rootdir / file_name
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

    for _, _, filenames in os.walk(fd):
        for name in filenames:
            try_delete_file(name)

    sd = utils.samples_dir()

    if not utils.check_dir(str(sd)):
        return

    for _, _, filenames in os.walk(sd):
        for name in filenames:
            try_delete_file(name, "sample")


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
        post = get_post(name=name)

        if post:
            do_delete_post(post)


def edit_post_title(ids: list[int], title: str, user: User) -> tuple[str, int]:
    if not ids:
        return utils.bad("Missing ids")

    if len(title) > config.max_title_length:
        return utils.bad("Title is too long")

    if not can_edit_post(ids, user):
        return utils.bad("You can't edit this")

    for post_id in ids:
        database.edit_post_title(post_id, title)

    return utils.ok("Title updated", {"title": title})


def edit_post_description(
    ids: list[int], description: str, user: User
) -> tuple[str, int]:
    if not ids:
        return utils.bad("Missing ids")

    description = utils.clean_description(description)

    if len(description) > config.max_description_length:
        return utils.bad("Description is too long")

    if not can_edit_post(ids, user):
        return utils.bad("You can't edit this")

    for post_id in ids:
        database.edit_post_description(post_id, description)

    return utils.ok("Description updated", {"description": description})


def edit_post_privacy(ids: list[int], privacy: str, user: User) -> tuple[str, int]:
    if not ids:
        return utils.bad("Missing ids")

    if privacy not in ["public", "private"]:
        return utils.bad("Invalid privacy setting")

    if not can_edit_post(ids, user):
        return utils.bad("You can't edit this")

    for post_id in ids:
        post = get_post(post_id)

        if not post:
            return utils.bad("Post not found")

        database.get_posts(file_hash=post.file_hash)
        database.edit_post_privacy(post_id, privacy)

    return utils.ok("Privacy updated")


def get_latest_post() -> Post | None:
    post = database.get_latest_post()

    if post:
        return make_post(post, utils.now(), False)

    return None


def get_post_update(post_id: int) -> tuple[bool, dict[str, Any]]:
    post = get_post(post_id, full=True, increase=False, full_reactions=True)

    if post:
        return True, {
            "title": post.title,
            "post_title": post.post_title,
            "uploader": post.uploader,
            "reactions": [r.to_dict() for r in post.reactions],
            "views": post.views,
        }

    return False, {}


def get_sample(name: str) -> Path | None:
    for file in utils.samples_dir().iterdir():
        if file.stem == name:
            return file

    return None


def can_edit_post(ids: list[int], user: User) -> bool:
    if user.admin:
        return True

    if not config.allow_edit:
        return False

    for post_id in ids:
        post = get_post(post_id)

        if not post:
            return False

        if post.username != user.username:
            return False

    return True
