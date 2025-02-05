from __future__ import annotations

# Standard
from typing import Any

# Libraries
from flask import Flask, render_template, request, Response  # type: ignore
from flask_cors import CORS  # type: ignore
from flask_simple_captcha import CAPTCHA  # type: ignore
from flask_limiter import Limiter  # type: ignore
from flask_limiter.util import get_remote_address  # type: ignore
from flask import send_from_directory  # pyright: ignore

# Modules
import config
import procs


# ---


app = Flask(__name__)

# Enable all cross origin requests
CORS(app)

simple_captcha = CAPTCHA(config=config.captcha)
app = simple_captcha.init_app(app)
rate_limit = f"{config.rate_limit} per minute"

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[rate_limit],
    storage_uri=f"redis://localhost:{config.redis_port}",
    strategy="fixed-window",
)


# ---


invalid = "Error: Invalid request"


# INDEX / UPLOAD


@app.route("/", methods=["POST", "GET"])  # type: ignore
@limiter.limit(rate_limit)  # type: ignore
def index() -> Any:
    if request.method == "POST":
        try:
            message = procs.upload(request)
            return render_template("message.html", message=message)
        except Exception:
            return Response(invalid, mimetype=config.text_mtype)

    if config.captcha_enabled:
        captcha = simple_captcha.create()
    else:
        captcha = None

    max_size = config.max_file_size
    show_code = bool(config.codes)

    return render_template(
        "index.html", captcha=captcha, max_size=max_size, show_code=show_code
    )


# SERVE FILE


@app.route("/files/<path:filename>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit)  # type: ignore
def get_file(filename: str) -> Any:
    return send_from_directory("files", filename)


# ADMIN


def check_password(password: str) -> bool:
    return bool(config.password) and (password == config.password)


@app.route("/admin/<password>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit)  # type: ignore
def admin(password: str) -> Any:
    if not check_password(password):
        return Response(invalid, mimetype=config.text_mtype)

    files = procs.get_files()
    return render_template("admin.html", files=files, password=password)


@app.route("/delete", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit)  # type: ignore
def delete() -> Any:
    data = request.get_json()
    name = data.get("name", None)
    password = data.get("password", None)

    if not check_password(password):
        return Response(invalid, mimetype=config.text_mtype)

    return procs.delete_file(name)


@app.route("/delete_all", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit)  # type: ignore
def delete_all() -> Any:
    data = request.get_json()
    password = data.get("password", None)

    if not check_password(password):
        return Response(invalid, mimetype=config.text_mtype)

    return procs.delete_all()
