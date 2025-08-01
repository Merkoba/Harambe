from __future__ import annotations

# Standard
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Libraries
from flask import jsonify  # type: ignore

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
    @staticmethod
    def is_image(mtype: str) -> bool:
        return mtype.startswith("image/")

    @staticmethod
    def is_video(mtype: str) -> bool:
        return mtype.startswith("video/")

    @staticmethod
    def is_audio(mtype: str) -> bool:
        return mtype.startswith("audio/")

    @staticmethod
    def is_flash(mtype: str) -> bool:
        return mtype.startswith("application/") and ("flash" in mtype)

    @staticmethod
    def is_text(mtype: str) -> bool:
        return (mtype.startswith("text/") and ("markdown" not in mtype)) or (
            mtype == "application/json"
        )

    @staticmethod
    def is_markdown(mtype: str) -> bool:
        return mtype.startswith("text/") and ("markdown" in mtype)

    @staticmethod
    def is_zip(mtype: str) -> bool:
        return mtype.startswith("application/") and ("zip" in mtype)

    @staticmethod
    def is_talk(mtype: str) -> bool:
        return mtype == "mode/talk"

    @staticmethod
    def is_url(mtype: str) -> bool:
        return mtype == "mode/url"

    @staticmethod
    def check_media(mtype: str, obj: Post | None = None) -> tuple[str, str]:
        media_type: str = ""
        sample_icon: str = ""

        if Post.is_text(mtype):
            media_type = "text"
            sample_icon = config.media_icons["text"]
        elif Post.is_markdown(mtype):
            media_type = "markdown"
            sample_icon = config.media_icons["markdown"]
        elif Post.is_zip(mtype):
            media_type = "zip"
            sample_icon = config.media_icons["zip"]
        elif Post.is_image(mtype):
            media_type = "image"
            sample_icon = config.media_icons["image"]
        elif Post.is_video(mtype):
            media_type = "video"
            sample_icon = config.media_icons["video"]
        elif Post.is_audio(mtype):
            media_type = "audio"
            sample_icon = config.media_icons["audio"]
        elif Post.is_flash(mtype):
            media_type = "flash"
            sample_icon = config.media_icons["flash"]
        elif Post.is_talk(mtype):
            media_type = "talk"
            sample_icon = config.media_icons["talk"]
        elif Post.is_url(mtype):
            media_type = "url"
            sample_icon = config.media_icons["url"]
        else:
            media_type = "unknown"
            sample_icon = config.media_icons["any"]
        if obj:
            if media_type:
                obj.media_type = media_type

            if sample_icon:
                obj.sample_icon = sample_icon

        return media_type, sample_icon

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
    description: str
    value: str
    has_url: bool
    youtube_id: str
    media_type: str = ""
    sample_icon: str = ""


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

    if all_data:
        description = post.description
    else:
        description = utils.striplimit(post.description, 280)

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

    is_text = mtype.startswith("text/")

    if is_text:
        markdown_embed = ("markdown" in mtype) and embed_size("markdown")
    else:
        markdown_embed = False

    zip_embed = mtype.startswith("application/") and ("zip" in mtype)
    file_hash = post.file_hash
    text = ""

    if all_data:
        text_file: Path | None = None

        if is_text:
            text_file = Path(utils.files_dir() / full)

        if (not text_file) or (not text_file.exists()):
            text_file = Path(utils.files_dir() / f"{name}.txt")

        if (not text_file) or (not text_file.exists()):
            text_file = Path(utils.samples_dir() / f"{name}.txt")

        if text_file and text_file.exists():
            max_bytes = config.embed_max_size_text * 1024 * 1024
            text = text_file.open("r").read(max_bytes)

    has_url = utils.is_url(text)
    youtube_id = ""

    if has_url:
        yt_info = utils.get_youtube_id(text)

        if yt_info and (yt_info[0] == "video"):
            youtube_id = yt_info[1]

    obj = Post(
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
        description,
        value,
        has_url,
        youtube_id,
    )

    Post.check_media(obj.mtype, obj)
    return obj


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
    random: bool = False,
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

        if media_type not in [None, "all"]:
            mtype = post.media_type
            mtypes = [media_type]

            if media_type == "text":
                mtypes.append("markdown")

            if mtype not in mtypes:
                continue

        total_size += post.size
        posts.append(post)

    total_size_str = utils.get_size(total_size)
    total_str = f"{total_size_str} ({len(posts)})"

    if random:
        utils.shuffle(posts)
    else:
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

    names: list[str] | None = None

    if name:
        names = [name]

    posts = database.get_posts(
        post_id=post_id,
        names=names,
        full_reactions=full_reactions,
        increase=increase,
    )

    post = posts[0] if posts else None

    if post:
        return make_post(post, utils.now(), full)

    return None


def get_prev_post(name: str) -> Post | None:
    if not name:
        return None

    db_post = database.get_prev_post(name)

    if db_post:
        return make_post(db_post, utils.now())

    return None


def get_next_post(post_id: int | None = None) -> Post | None:
    db_post = database.get_next_post(post_id)

    if db_post:
        return make_post(db_post, utils.now())

    return None


def get_next_post_by_type(post_type: str, post_id: int | None = None) -> Post | None:
    func = getattr(database, f"get_next_{post_type}_post", lambda: None)
    db_post = func(post_id)

    if db_post:
        return make_post(db_post, utils.now())

    return None


def get_random_post(used_ids: list[int]) -> Post | None:
    db_post = database.get_random_post(used_ids)

    if db_post:
        return make_post(db_post, utils.now())

    return None


def get_random_post_by_type(post_type: str) -> Post | None:
    db_post = getattr(database, f"get_random_{post_type}_post", lambda: None)()

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

    if not title:
        return utils.bad("Missing title")

    if utils.is_url(title, True):
        return utils.bad("Title can't be a URL")

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
        posts = database.get_posts(post_id)
        post = posts[0] if posts else None

        if not post:
            return utils.bad("Post not found")

        if (not description) and (post.mtype == "mode/talk"):
            return utils.bad("Description can't be empty")

        database.edit_post_description(post_id, description)

    return utils.ok("Description updated", {"description": description})


def edit_post_filename(ids: list[int], filename: str, user: User) -> tuple[str, int]:
    if not ids:
        return utils.bad("Missing ids")

    filename = utils.clean_full_filename(filename)

    if len(filename) > config.max_filename_length:
        return utils.bad("Filename is too long")

    if not can_edit_post(ids, user):
        return utils.bad("You can't edit this")

    original, ext = utils.ext_split(filename)

    for post_id in ids:
        posts = database.get_posts(post_id)
        post = posts[0] if posts else None

        if not post:
            return utils.bad("Post not found")

        if (not filename) and (post.mtype == "mode/talk"):
            return utils.bad("Filename can't be empty")

        if original:
            database.edit_post_original(post_id, original)

        if ext:
            database.edit_post_ext(post_id, ext)

        old_filename = get_original_name(post.original, post)
        rename_file(old_filename, filename)

    return utils.ok(
        "Filename updated", {"original": original, "original_full": filename}
    )


def edit_post_privacy(ids: list[int], privacy: str, user: User) -> tuple[str, int]:
    if not ids:
        return utils.bad("Missing ids")

    if privacy not in ["public", "private"]:
        return utils.bad("Invalid privacy setting")

    if not can_edit_post(ids, user):
        return utils.bad("You can't edit this")

    for post_id in ids:
        posts = database.get_posts(post_id)
        post = posts[0] if posts else None

        if not post:
            return utils.bad("Post not found")

        if post.value:
            if not config.allow_same_value:
                exists = database.get_posts(value=post.value, ignore_ids=[post.id])

                if exists:
                    return utils.bad("Post with same value already exists")
        elif post.size and post.file_hash:
            if not config.allow_same_hash:
                exists = database.get_posts(
                    file_hash=post.file_hash, ignore_ids=[post.id]
                )

                if exists:
                    return utils.bad("Post with same file hash already exists")
        elif post.title and post.description:
            if not config.allow_same_talk:
                exists = database.get_posts(
                    title=post.title, description=post.description, ignore_ids=[post.id]
                )

                if exists:
                    return utils.bad("Same talk already exists")

        database.edit_post_privacy(post.id, privacy)

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


def get_data(name: str) -> Any:
    if not name:
        return jsonify({"error": "Post id is required"})

    post = get_post(name=name)

    if not post:
        return jsonify({"error": "Post not found"})

    return post_to_json(post)


def post_to_json(post: Post) -> Any:
    return jsonify(
        {
            "id": post.id,
            "name": post.name,
            "full": post.full,
            "ext": post.ext,
            "mtype": post.mtype,
            "size": post.size,
            "views": post.views,
            "title": post.title,
            "description": post.description,
            "privacy": post.privacy,
            "filename": post.original_full,
        }
    )


def rename_file(old_name: str, new_name: str) -> None:
    if not old_name or not new_name:
        return

    old_path = utils.files_dir() / old_name
    new_path = utils.files_dir() / new_name

    if not old_path.exists():
        return

    if old_path == new_path:
        return

    if new_path.exists():
        return

    try:
        old_path.rename(new_path)
    except OSError as e:
        utils.log(f"Error renaming file {old_name} to {new_name}: {e}")
