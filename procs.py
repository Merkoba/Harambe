from __future__ import annotations

# Standard
from typing import Any
from pathlib import Path

# Modules
import app
import utils
import config


def error(s: str) -> str:
    return f"Error: {s}"


def upload(request: Any) -> str:
    file = request.files.get("file", None)
    c_hash = request.form.get("captcha-hash", "")
    c_text = request.form.get("captcha-text", "")
    code = request.form.get("code", "")

    if config.captcha_enabled:
        check_catpcha = True

        if config.captcha_cheat and (c_text == config.captcha_cheat):
            check_catpcha = False

        if check_catpcha:
            if not app.simple_captcha.verify(c_text, c_hash):
                return error("Failed captcha")

    if config.code and (code != config.code):
        return error("Invalid code")

    if not file:
        return error("No file")

    if file:
        if hasattr(file, "read"):
            try:
                content = file.read()
                length = len(content)

                if length > config.max_file_size:
                    return error("File is too big")

                if content:
                    file.seek(0)
                    fname = file.filename
                    split = fname.split(".")

                    if len(split) < 2:
                        return error("File has no extension")

                    ext = split[-1]
                    name = split[0]
                    name = utils.file_name(name, config.file_name_max)
                    name = f"{name}_{int(utils.now())}_{utils.numstring(3)}"
                    new_name = f"{name}.{ext}"
                    path = f"files/{new_name}"

                    try:
                        file.save(path)
                    except Exception:
                        return error("Failed to save file")

                    mb = round(length / 1_000_000, 2)
                    return f'Uploaded: <a href="/{path}">{new_name}</a> ({mb} mb)'

                return error("File is empty")
            except Exception:
                return error("Failed to read file")
        else:
            return error("File object has no 'read' attribute")
    else:
        return error("File is None")

    return error("Nothing was uploaded")


def get_files() -> list[str]:
    files = list(Path("files").glob("*"))
    files = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
    files = files[: config.admin_max_files]
    return [f.name for f in files if not f.name.startswith(".")]
