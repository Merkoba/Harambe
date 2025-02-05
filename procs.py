from __future__ import annotations

# Standard
from typing import Any
from pathlib import Path

# Libraries
from flask import jsonify  # type: ignore

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


def get_files() -> list[dict[str, Any]]:
    files = list(Path("files").glob("*"))
    files = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
    files = files[: config.admin_max_files]

    return [
        {
            "name": f.name,
            "size": utils.get_size(f.stat().st_size),
        }
        for f in files
        if not f.name.startswith(".")
    ]


def delete_file(name: str) -> tuple[str, int]:
    if not name:
        return jsonify({"status": "error", "message": "Filename is required"}), 400

    if name.startswith("."):
        return jsonify({"status": "error", "message": "Invalid filename"}), 400

    try:
        do_delete_file(name)
        return jsonify({"status": "ok", "message": "File deleted successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def do_delete_file(name: str) -> None:
    path = f"files/{name}"
    file = Path(path)

    if file.exists():
        file.unlink()


def delete_all() -> tuple[str, int]:
    try:
        do_delete_all()
        return jsonify(
            {"status": "ok", "message": "All files deleted successfully"}
        ), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def do_delete_all() -> None:
    files = Path("files").glob("*")

    for file in files:
        if file.name.startswith("."):
            continue

        file.unlink()
