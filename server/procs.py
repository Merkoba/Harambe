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


def error(s: str) -> dict[str, str]:
    return {"message": f"Error: {s}", "mode": "error", "data": ""}


def upload(request: Any) -> dict[str, str]:
    file = request.files.get("file", None)
    c_hash = request.form.get("captcha-hash", "")
    c_text = request.form.get("captcha-text", "")
    code = request.form.get("code", "")

    if config.codes and (code not in config.codes):
        return error("Invalid code")

    if config.captcha_enabled:
        check_catpcha = True

        if config.captcha_cheat and (c_text == config.captcha_cheat):
            check_catpcha = False

        if check_catpcha:
            if not app.simple_captcha.verify(c_text, c_hash):
                return error("Failed captcha")

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
                    pfile = Path(fname)
                    ext = pfile.suffix
                    name = pfile.stem
                    name = utils.file_name(name, config.file_name_max)
                    name = f"{name}_{int(utils.now())}_{utils.numstring(3)}"

                    if ext:
                        new_name = f"{name}{ext}"
                    else:
                        new_name = name

                    path = utils.files_dir() / new_name
                    fpath = str(Path("files") / new_name)

                    try:
                        file.save(path)
                    except Exception:
                        return error("Failed to save file")

                    mb = round(length / 1_000_000, 2)
                    m = f'Uploaded: <a class="link" href="/{fpath}">{new_name}</a> ({mb} mb)'
                    return {"message": m, "mode": "upload", "data": fpath}

                return error("File is empty")
            except Exception as e:
                utils.error(e)
                return error("Failed to read file")
        else:
            return error("File object has no 'read' attribute")
    else:
        return error("File is None")

    return error("Nothing was uploaded")


def time_ago(date: float) -> str:
    return utils.time_ago(date, utils.now())


def get_files() -> list[dict[str, Any]]:
    files = list(utils.files_dir().glob("*"))
    files = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
    files = files[: config.admin_max_files]

    return [
        {
            "name": f.name,
            "size": utils.get_size(f.stat().st_size),
            "ago": time_ago(f.stat().st_mtime),
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
    path = utils.files_dir() / name
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
    files = utils.files_dir().glob("*")

    for file in files:
        if file.name.startswith("."):
            continue

        file.unlink()
