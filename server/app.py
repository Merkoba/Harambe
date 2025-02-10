from __future__ import annotations

# Standard
from typing import Any
from functools import wraps

# Libraries
from flask import Flask, render_template, request, Response  # type: ignore
from flask import send_from_directory, redirect, url_for, session, flash  # pyright: ignore
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

simple_captcha = CAPTCHA(config=config.get_captcha())
app = simple_captcha.init_app(app)


def logged_in() -> bool:
    return bool(session.get("username"))


def login_required(f: Any) -> Any:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not logged_in():
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


def rate_limit(n: int) -> str:
    return f"{n} per minute"


limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[rate_limit(config.rate_limit)],
    storage_uri=f"redis://localhost:{config.redis_port}",
    strategy="fixed-window",
)

invalid = "Error: Invalid request"
text_mtype = "text/plain"


# INDEX / UPLOAD


@app.route("/", methods=["POST", "GET"], strict_slashes=False)  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
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

    logged = logged_in()
    link_list = config.list_enabled and (config.link_list or logged)

    return render_template(
        "index.html",
        captcha=captcha,
        link_list=link_list,
        link_admin=logged,
        image_name=procs.get_image_name(),
        max_size=config.get_max_file_size(),
        max_file_size=config.max_file_size,
        show_max_file_size=config.show_max_file_size,
        require_key=config.require_key,
        show_image=config.show_image,
        background_color=config.background_color,
        accent_color=config.accent_color,
        font_color=config.font_color,
        text_color=config.text_color,
        link_color=config.link_color,
        font_family=config.font_family,
        main_title=config.main_title,
        image_tooltip=config.image_tooltip,
    )


@app.route("/upload", methods=["POST"], strict_slashes=False)  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
def upload() -> Any:
    return procs.upload(request, "cli").message


@app.route("/message", methods=["GET"], strict_slashes=False)  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
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

    background_color = config.background_color
    accent_color = config.accent_color
    font_color = config.font_color
    text_color = config.text_color
    link_color = config.link_color
    font_family = config.font_family
    m = Message(data["message"], data["mode"], data["data"])

    return render_template(
        "message.html",
        mode=m.mode,
        message=m.message,
        data=m.data,
        background_color=background_color,
        accent_color=accent_color,
        font_color=font_color,
        text_color=text_color,
        link_color=link_color,
        font_family=font_family,
    )


# SERVE FILE


@app.route(
    f"/{config.file_path}/<path:filename>", methods=["GET"], strict_slashes=False
)  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
def get_file(filename: str) -> Any:
    fd = utils.files_dir()
    return send_from_directory(fd, filename, max_age=config.max_age)


# ADMIN


@app.route("/admin", defaults={"page": 1}, methods=["GET"], strict_slashes=False)  # type: ignore
@app.route("/admin/<int:page>", methods=["GET"], strict_slashes=False)  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@login_required
def admin(page: int = 1) -> Any:
    page_size = request.args.get("page_size", config.admin_page_size)
    files, total, next_page = procs.get_files(page, page_size)
    def_page_size = page_size == config.admin_page_size

    return render_template(
        "admin.html",
        files=files,
        total=total,
        page=page,
        next_page=next_page,
        page_size=page_size,
        def_page_size=def_page_size,
        file_path=config.file_path,
    )


@app.route("/delete_files", methods=["POST"], strict_slashes=False)  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@login_required
def delete_files() -> Any:
    data = request.get_json()
    files = data.get("files", None)
    return procs.delete_files(files)


@app.route("/delete_all_files", methods=["POST"], strict_slashes=False)  # type: ignore
@limiter.limit(rate_limit(3))  # type: ignore
@login_required
def delete_all() -> Any:
    return procs.delete_all()


# AUTH


@app.route("/login", methods=["GET", "POST"], strict_slashes=False)  # type: ignore
@limiter.limit(rate_limit(3))  # type: ignore
def login() -> Any:
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if (not username) or (not password):
            flash("Invalid credentials")
            return redirect(url_for("login"))

        if config.check_user(username, password):
            session["username"] = username
            return redirect(url_for("admin"))

        flash("Invalid credentials")

    return render_template("login.html")


@app.route("/logout", methods=["GET"], strict_slashes=False)  # type: ignore
@limiter.limit(rate_limit(3))  # type: ignore
def logout() -> Any:
    session.pop("username", None)
    return redirect(url_for("index"))


# PUBLIC LIST


@app.route("/list", defaults={"page": 1}, methods=["GET"], strict_slashes=False)  # type: ignore
@app.route("/list/<int:page>", methods=["GET"], strict_slashes=False)  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
def show_list(page: int = 1) -> Any:
    pw = request.args.get("pw", "")

    if not logged_in():
        if not config.list_enabled:
            return redirect(url_for("index"))

        if config.list_password and (pw != config.list_password):
            return redirect(url_for("index"))

    page_size = request.args.get("page_size", config.list_page_size)
    files, total, next_page = procs.get_files(page, page_size)
    def_page_size = page_size == config.list_page_size
    use_password = bool(pw)

    return render_template(
        "list.html",
        files=files,
        total=total,
        page=page,
        next_page=next_page,
        page_size=page_size,
        def_page_size=def_page_size,
        password=pw,
        use_password=use_password,
        file_path=config.file_path,
    )
