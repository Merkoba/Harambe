from __future__ import annotations

# Standard
import zipfile
import hashlib
import mimetypes
from typing import Any
from pathlib import Path
from io import BytesIO

# Libraries
import ulid  # type: ignore
from flask import Request  # type: ignore
from werkzeug.datastructures import FileStorage  # type: ignore

# Modules
import utils
import database
import post_procs
import user_procs
import magic_procs
import sample_procs
from config import config
from user_procs import User


MadeURL = tuple[str, str, bytes | None, str]


def error(s: str) -> tuple[bool, str]:
    return False, f"Error: {s}"


def get_name(user: User) -> str:
    u = ulid.new()
    name = str(u.str)[: config.get_post_name_length()].strip()

    if user.mark:
        name = f"{name}_{user.mark}".strip()

    if not config.uppercase_names:
        name = name.lower()

    return name


def make_zip(files: list[FileStorage]) -> bytes:
    buffer = BytesIO()
    clevel = config.zip_level
    fixed_time = (1980, 1, 1, 0, 0, 0)

    with zipfile.ZipFile(
        buffer, "w", zipfile.ZIP_DEFLATED, compresslevel=clevel
    ) as zipf:
        for file in sorted(files, key=lambda f: f.filename):
            content = file.read()
            filename = Path(file.filename).name
            zip_info = zipfile.ZipInfo(filename)
            zip_info.date_time = fixed_time
            zip_info.comment = b""
            zip_info.extra = b""
            zip_info.create_system = 0
            zip_info.create_version = 20
            zip_info.extract_version = 20
            zip_info.external_attr = 0
            zipf.writestr(zip_info, content)
            file.seek(0)

    buffer.seek(0)
    return buffer.getvalue()


def check_hash(content: bytes) -> tuple[str, str]:
    file_hash = hashlib.sha256(content).hexdigest()

    if not config.allow_same_hash:
        existing = database.get_posts(file_hash=file_hash)

        if existing:
            return file_hash, existing[0].name

    return file_hash, ""


def make_file(
    text: str, filename: str, files: list[FileStorage], seen_files: set[str]
) -> None:
    text_io = BytesIO(text.encode("utf-8"))
    mtype, _ = mimetypes.guess_type(filename)
    mtype = mtype or "text/plain"

    text_file = FileStorage(
        stream=text_io,
        filename=filename,
        name="file",
        content_type=mtype,
    )

    files.append(text_file)
    seen_files.add(filename)


def make_url_file(
    url: str, files: list[FileStorage], seen_files: set[str]
) -> MadeURL | None:
    if not url:
        return None

    if len(url) > config.max_url_length:
        return None

    make_file(url, "url.txt", files, seen_files)

    if config.fetch_youtube and utils.is_youtube_url(url):
        ans_1 = utils.get_youtube_info(url)

        if ans_1:
            title, description, content = ans_1
            return title, description, content, "jpg"
    elif config.fetch_url:
        ans_2 = utils.get_url_info(url)
        info = url
        title = ""
        description = ""

        if ans_2:
            if ans_2[0]:
                title = ans_2[0]
                info += f"\n\n{ans_2[0]}"

            if ans_2[1]:
                info += f"\n\n{ans_2[1]}"
                description = ans_2[1]

        content = info.encode("utf-8")

        if len(content) > config.sample_text_bytes:
            content = content[: config.sample_text_bytes]

        return title, description, content, "txt"

    return None


def make_empty_file(files: list[FileStorage], seen_files: set[str]) -> None:
    empty_file = FileStorage(
        stream=BytesIO(b""),
        filename="empty.txt",
        name="file",
        content_type="text/plain",
    )

    files.append(empty_file)
    seen_files.add("empty.txt")


def make_archive_files(
    archive_info: list[tuple[str, bytes, int]], files: list[FileStorage], seen_files: set[str]
) -> None:
    for filename, content, size in archive_info:
        if filename in seen_files:
            continue

        mtype, _ = mimetypes.guess_type(filename)
        mtype = mtype or "application/octet-stream"
        content_stream = BytesIO(content)

        archive_file = FileStorage(
            stream=content_stream,
            filename=filename,
            name="file",
            content_type=mtype,
        )

        files.append(archive_file)
        seen_files.add(filename)


def make_text_files(
    request: Request, files: list[FileStorage], seen_files: set[str]
) -> None:
    pastebins = request.form.getlist("pastebin")

    for index, otext in enumerate(pastebins):
        text = utils.clean_pastebin(otext)

        if not text:
            continue

        if len(text) > config.max_pastebin_length:
            continue

        filename = request.form.getlist("pastebin_filename")[index].strip()

        if not filename:
            if len(pastebins) == 1:
                filename = "paste.txt"
            else:
                filename = f"paste_{index + 1}.txt"

        filename = utils.fix_filename(filename)
        make_file(text, filename, files, seen_files)


def upload(request: Any, user: User, mode: str = "normal") -> tuple[bool, str]:
    if not user:
        return error("No user")

    u_ok, u_msg = user_procs.check_user_limit(user)

    if not u_ok:
        return error(u_msg)

    title = request.form.get("title", "")
    files: list[FileStorage] = []
    seen_files: set[str] = set()
    presample: bytes | None = None
    presample_ext = ""
    description = utils.clean_description(request.form.get("description", ""))
    privacy = request.form.get("privacy", "public")
    value = ""
    mtype = ""

    if privacy not in ["public", "private"]:
        return error("Invalid privacy setting")

    if utils.is_url(title):
        if not config.allow_same_value:
            eposts = database.get_posts(value=title)
            epost = eposts[0] if eposts else None

            if epost and (privacy == "public"):
                return return_post(epost.name, privacy)

        ans: MadeURL | None = make_url_file(title, files, seen_files)

        if ans:
            value = title

            if ans[0]:
                title = ans[0][: config.max_title_length].strip()

            if ans[1]:
                if not description:
                    description = utils.clean_description(ans[1])

            if ans[2]:
                presample = ans[2]
                presample_ext = ans[3]

            mtype = "mode/url"
        else:
            return error("Failed to fetch URL")
    elif utils.contains_url(title):
        return error("Title contains a URL")

    if len(title) > config.max_title_length:
        return error("Title is too long")

    if len(description) > config.max_description_length:
        return error("Description is too long")

    if config.pastebin_enabled:
        make_text_files(request, files, seen_files)

    for file in request.files.getlist("file"):
        if file and file.filename:
            filename = Path(file.filename).name

            if filename and (filename not in seen_files):
                seen_files.add(filename)
                files.append(file)

    if len(files) == 0:
        if not description:
            return error("No file or description")

        if not config.allow_same_talk:
            exists = database.get_posts(title=title, description=description)

            if exists and (privacy == "public"):
                return error("Same talk already exists")

        make_empty_file(files, seen_files)
        psample = ""

        if title:
            psample = title

        if description:
            psample += f"\n\n{description}"

        presample = psample.encode("utf-8")
        presample_ext = "txt"
        mtype = "mode/talk"

    if (len(files) < 1) or (len(files) > config.max_upload_files):
        return error("Wrong file length")

    total_size = 0

    for file in files:
        if not file.name:
            return error("No file name")

        if len(file.name) > 255:
            return error("File name is too long")

        if not hasattr(file, "read"):
            return error("File object has no 'read' attribute")

        file.seek(0, 2)
        total_size += file.tell()
        file.seek(0)

    if not user_procs.check_user_max(user, total_size):
        return error("Upload is too big")

    post_name = get_name(user)
    zip_archive = utils.get_checkbox(request, "zip")

    image_magic = False
    audio_magic = False
    video_magic = False
    album_magic = False
    visual_magic = False
    gif_magic = False

    if len(files) == 1:
        if config.magic_enabled:
            if magic_procs.is_image_magic(request, files[0]):
                image_magic = True
            elif magic_procs.is_audio_magic(request, files[0]):
                audio_magic = True
            elif magic_procs.is_video_magic(request, files[0]):
                video_magic = True
    elif len(files) > 1:
        if (
            user.mage
            and config.magic_enabled
            and magic_procs.is_album_magic(request, files)
        ):
            album_magic = True
        elif (
            user.mage
            and config.magic_enabled
            and magic_procs.is_visual_magic(request, files)
        ):
            visual_magic = True
        elif (
            user.mage
            and config.magic_enabled
            and magic_procs.is_gif_magic(request, files)
        ):
            gif_magic = True
        else:
            zip_archive = True

    if (
        image_magic
        or audio_magic
        or video_magic
        or album_magic
        or visual_magic
        or gif_magic
    ):
        zip_archive = False

    if zip_archive:
        try:
            content = make_zip(files)
            ext = ".zip"

        except Exception as e:
            utils.error(e)
            return error("Failed to zip files")
    elif image_magic:
        result = magic_procs.do_magic("image", files)

        if not result:
            return error("Failed to do image magic")

        content, ext = result
    elif audio_magic:
        result = magic_procs.do_magic("audio", files)

        if not result:
            return error("Failed to do audio magic")

        content, ext = result
    elif video_magic:
        result = magic_procs.do_magic("video", files)

        if not result:
            return error("Failed to do video magic")

        content, ext = result
    elif album_magic:
        result = magic_procs.do_magic("album", files)

        if not result:
            return error("Failed to do album magic")

        content, ext = result
    elif visual_magic:
        result = magic_procs.do_magic("visual", files)

        if not result:
            return error("Failed to do visual magic")

        content, ext = result
    elif gif_magic:
        result = magic_procs.do_magic("gif", files)

        if not result:
            return error("Failed to do gif magic")

        content, ext = result
    else:
        file = files[0]
        content = file.read()
        filename = file.filename or ""
        ext = Path(filename).suffix.lower()
        archfiles = utils.read_archive(content, filename)

        if archfiles:
            original_content = content
            zip_archive = True
            files.clear()
            seen_files.clear()
            make_archive_files(archfiles, files, seen_files)
            content = original_content

    file_hash, existing = check_hash(content)

    if existing and (privacy == "public") and content:
        if mode == "normal":
            return True, existing

    try:
        full_name = post_name + ext if ext else post_name
        path = utils.files_dir() / Path(full_name)
        path.write_bytes(content)
    except Exception as e:
        utils.error(e)
        return error("Failed to save file")

    file_size = path.stat().st_size

    if not mtype:
        mt, _ = mimetypes.guess_type(path)
        mtype = mt or ""

    if zip_archive and title and (len(files) > 1):
        original = title
    else:
        original = Path(files[0].filename).stem

    original = utils.clean_filename(original)

    database.add_post(
        user_id=user.id,
        name=post_name,
        ext=ext[1:],
        title=title,
        original=original,
        mtype=mtype,
        size=file_size,
        file_hash=file_hash,
        privacy=privacy,
        description=description,
        value=value,
    )

    if config.remove_metadata:
        try:
            utils.remove_metadata(path)
        except Exception as e:
            utils.error(e)

    if config.samples_enabled:
        if presample:
            sample_procs.save_presample(path, presample, presample_ext)
        else:
            sample_procs.make_sample(path, files, mtype, zip_archive)

    database.update_user_last_date(user.id)
    post_procs.check_storage()
    return return_post(post_name, privacy)


def return_post(name: str, privacy: str) -> tuple[bool, str]:
    if privacy == "private":
        if config.mark_private_posts:
            mark = config.private_posts_mark
            name = f"{name}?{mark}=true"

    return True, name


def api_upload(request: Request) -> tuple[bool, str]:
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    if (not username) or (not password):
        return error("Missing username or password")

    if (len(username) > 255) or (len(password) > 255):
        return error("Invalid username or password")

    user = user_procs.check_auth(username, password)

    if not user:
        return error("Invalid username or password")

    return upload(request, user, "cli")
