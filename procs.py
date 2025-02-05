from __future__ import annotations

# Standard
from flask import jsonify, Response  # type: ignore
from typing import Any

# Modules
import app as App
import utils as Utils
import config as Config


def upload(request: Any) -> str:
    file = request.files.get("file", None)
    c_hash = request.form.get("captcha-hash", "")
    c_text = request.form.get("captcha-text", "")
    code = request.form.get("code", "")

    check_catpcha = True

    if Config.captcha_cheat and (c_text == Config.captcha_cheat):
        check_catpcha = False

    if check_catpcha:
        if not App.simple_captcha.verify(c_text, c_hash):
            return "Error: Failed captcha"

    if code != Config.code:
        return "Error: Invalid code"

    if not file:
        return "Error: No file"

    if file:
        if hasattr(file, "read"):
            try:
                content = file.read()
                length = len(content)

                if length > Config.max_file_size:
                    return "Error: File too big"

                if content:
                    file.seek(0)
                    fname = file.filename
                    split = fname.split(".")

                    if len(split) < 2:
                        return "Error: File has no extension"

                    ext = split[-1]
                    name = split[0]
                    name = Utils.file_name(name, Config.file_name_max)
                    name = f"{name}_{int(Utils.now())}_{Utils.numstring(3)}"
                    new_name = f"{name}.{ext}"
                    path = f"files/{new_name}"

                    try:
                        file.save(path)
                    except Exception as e:
                        return f"Error: Failed to save file - {e}"

                    mb = round(length / 1_000_000, 2)
                    return f'Uploaded: <a href="/{path}">{new_name}</a> ({mb} mb)'
                else:
                    return "Error: File is empty"
            except Exception as e:
                return f"Error: Failed to read file - {e}"
        else:
            return "Error: File object has no 'read' attribute"
    else:
        return "Error: File is None"

    return "Error: Nothing was uploaded"
