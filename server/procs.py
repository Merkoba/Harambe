from __future__ import annotations

# Standard
import mimetypes
from typing import Any
from pathlib import Path

# Libraries
from flask import jsonify  # type: ignore
import ulid  # type: ignore

# Modules
import app
import utils
import database
from config import config
import user_procs
from user_procs import User
import file_procs


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

        u_ok, u_msg = user_procs.check_user_limit(user)

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

            if user:
                if not user_procs.check_user_max(user, length):
                    return error(toobig)
            elif length > config.max_size_anon:
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
                        listed = user.lister
                    else:
                        uploader = ""
                        listed = config.anon_listers

                    mtype, _ = mimetypes.guess_type(path)
                    mtype = mtype or ""

                    if mtype.startswith("text"):
                        sample = content[: config.sample_size].decode(
                            "utf-8", errors="ignore"
                        )
                    else:
                        sample = ""

                    database.add_file(
                        name,
                        cext,
                        title,
                        pfile.stem,
                        username,
                        uploader,
                        mtype,
                        listed,
                        length,
                        sample,
                    )

                    database.update_user_last_date(username)
                except Exception as e:
                    utils.error(e)
                    return error("Failed to save file")

                file_procs.check_storage()

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


def get_image_name() -> str:
    if Path("static/img/banner.jpg").exists():
        return "banner.jpg"

    if Path("static/img/banner.png").exists():
        return "banner.png"

    if Path("static/img/banner.gif").exists():
        return "banner.gif"

    return "cat.jpg"


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
