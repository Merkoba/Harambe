from __future__ import annotations

# Standard
from typing import Any

# Libraries
from flask import Flask, render_template, request, Response  # type: ignore
from flask import send_from_directory, redirect, url_for, session  # pyright: ignore
from flask_cors import CORS  # type: ignore
from flask_simple_captcha import CAPTCHA  # type: ignore
from flask_limiter import Limiter  # type: ignore
from flask_limiter.util import get_remote_address  # type: ignore

# Modules
import procs
import utils
from procs import Message
from config import config


# ---


app = Flask(__name__)
app.secret_key = config.app_key
app.config["MAX_CONTENT_LENGTH"] = config.get_max_file_size()

# Enable all cross origin requests
CORS(app)

simple_captcha = CAPTCHA(config=config.captcha)
app = simple_captcha.init_app(app)


def rate_limit(n: int) -> str:
    return f"{n} per minute"


limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[rate_limit(12)],
    storage_uri=f"redis://localhost:{config.redis_port}",
    strategy="fixed-window",
)

invalid = "Error: Invalid request"
text_mtype = "text/plain"


# INDEX / UPLOAD


@app.route("/", methods=["POST", "GET"])  # type: ignore
@limiter.limit(rate_limit(12))  # type: ignore
def index() -> Any:
    if request.method == "POST":
        try:
            m = session["data"] = procs.upload(request)

            data = {
                "mode": m.mode,
                "message": m.message,
                "data": m.data,
            }

            session["data"] = data
            return redirect(url_for("message"))

        except Exception as e:
            utils.error(e)
            return Response(invalid, mimetype=text_mtype)

    if config.require_captcha:
        captcha = simple_captcha.create()
    else:
        captcha = None

    max_size = config.get_max_file_size()
    require_key = config.require_key
    show_image = config.show_image

    return render_template(
        "index.html",
        captcha=captcha,
        max_size=max_size,
        require_key=require_key,
        show_image=show_image,
    )


@app.route("/upload", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.key_limit))  # type: ignore
def upload() -> Any:
    return procs.upload(request, "cli").message


@app.route("/message", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(12))  # type: ignore
def message() -> Any:
    data = {}
    ok = True

    if "data" in session:
        data = session.get("data")

        if not data:
            ok = False
    else:
        ok = False

    if not ok:
        return redirect(url_for("index"))

    m = Message(data["message"], data["mode"], data["data"])
    return render_template("message.html", mode=m.mode, message=m.message, data=m.data)


# SERVE FILE


@app.route("/file/<path:filename>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(12))  # type: ignore
def get_file(filename: str) -> Any:
    fd = utils.files_dir()
    return send_from_directory(fd, filename)


# ADMIN


@app.route("/dashboard/<string:password>", defaults={"page": 1}, methods=["GET"])  # type: ignore
@app.route("/dashboard/<string:password>/<int:page>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(12))  # type: ignore
def dashboard(password: str, page: int = 1) -> Any:
    if not procs.check_password(password):
        return Response(invalid, mimetype=text_mtype)

    files, total, next_page = procs.dashboard(page)
    return render_template(
        "dashboard.html",
        files=files,
        password=password,
        total=total,
        page=page,
        next_page=next_page,
    )


@app.route("/delete", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(12))  # type: ignore
def delete() -> Any:
    data = request.get_json()
    name = data.get("name", None)
    password = data.get("password", None)

    if not procs.check_password(password):
        return Response(invalid, mimetype=text_mtype)

    return procs.delete_file(name)


@app.route("/delete_all", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(3))  # type: ignore
def delete_all() -> Any:
    data = request.get_json()
    password = data.get("password", None)

    if not procs.check_password(password):
        return Response(invalid, mimetype=text_mtype)

    return procs.delete_all()
