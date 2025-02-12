from __future__ import annotations

# Standard
from typing import Any
from functools import wraps

# Libraries
from flask import Flask, render_template, request, Response, send_file  # type: ignore
from flask import redirect, url_for, session, flash  # pyright: ignore
from flask_cors import CORS  # type: ignore
from flask_simple_captcha import CAPTCHA  # type: ignore
from flask_limiter import Limiter  # type: ignore
from flask_limiter.util import get_remote_address  # type: ignore

# Modules
import procs
import utils
from config import config


app = Flask(__name__)
app.url_map.strict_slashes = False
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


@app.route("/", methods=["POST", "GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
def index() -> Any:
    if not config.web_uploads_enabled:
        return render_template("fallback.html")

    if request.method == "POST":
        try:
            ok, ans = procs.upload(request)

            if not ok:
                data = {
                    "mode": "error",
                    "message": ans,
                }

                session["data"] = data
                return redirect(url_for("message"))

            return redirect(url_for("post", name=ans))

        except Exception as e:
            utils.error(e)
            return Response(invalid, mimetype=text_mtype)

    if config.require_captcha:
        captcha = simple_captcha.create()
    else:
        captcha = None

    return render_template(
        "index.html",
        captcha=captcha,
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
        max_comment_length=config.max_comment_length,
        allow_comments=config.allow_comments,
        links=config.links,
    )


@app.route("/upload", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
def api_upload() -> Any:
    if not config.api_uploads_enabled:
        return "error"

    _, msg = procs.upload(request, "cli")
    return msg


@app.route("/message", methods=["GET"])  # type: ignore
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

    return render_template(
        "message.html",
        mode=data["mode"],
        message=data["message"],
        background_color=background_color,
        accent_color=accent_color,
        font_color=font_color,
        text_color=text_color,
        link_color=link_color,
        font_family=font_family,
    )


# SERVE FILE


@app.route("/post/<string:name>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
def post(name: str) -> Any:
    file = procs.get_file(name)

    if not file:
        return Response(invalid, mimetype=text_mtype)

    return render_template(
        "post.html",
        file=file,
        file_path=config.file_path,
        background_color=config.background_color,
        accent_color=config.accent_color,
        font_color=config.font_color,
        text_color=config.text_color,
        link_color=config.link_color,
        font_family=config.font_family,
    )


@app.route(f"/{config.file_path}/<path:name>", methods=["GET"])  # type: ignore
@app.route(f"/{config.file_path}/<path:name>/<string:original>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
def get_file(name: str, original: str | None = None) -> Any:
    file = procs.get_file(name)

    if not file:
        return Response(invalid, mimetype=text_mtype)

    fd = utils.files_dir()
    return send_file(fd / file.full, download_name=original, max_age=config.max_age)


# ADMIN


@app.route("/admin", defaults={"page": 1}, methods=["GET"])  # type: ignore
@app.route("/admin/<int:page>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@login_required
def admin(page: int = 1) -> Any:
    query = request.args.get("query", "")
    sort = request.args.get("sort", "date")
    page_size = request.args.get("page_size", config.admin_page_size)
    files, total, next_page = procs.get_files(page, page_size, query=query, sort=sort)
    def_page_size = page_size == config.admin_page_size

    return render_template(
        "admin.html",
        files=files,
        total=total,
        page=page,
        next_page=next_page,
        page_size=page_size,
        def_page_size=def_page_size,
    )


@app.route("/delete_files", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@login_required
def delete_files() -> Any:
    data = request.get_json()
    files = data.get("files", None)
    return procs.delete_files(files)


@app.route("/delete_all_files", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(3))  # type: ignore
@login_required
def delete_all() -> Any:
    return procs.delete_all()


# AUTH


@app.route("/login", methods=["GET", "POST"])  # type: ignore
@limiter.limit(rate_limit(3))  # type: ignore
def login() -> Any:
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if (not username) or (not password):
            flash("Invalid credentials")
            return redirect(url_for("login"))

        if config.check_admin(username, password):
            session["username"] = username
            return redirect(url_for("admin"))

        flash("Invalid credentials")

    return render_template("login.html")


@app.route("/logout", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(3))  # type: ignore
def logout() -> Any:
    session.pop("username", None)
    return redirect(url_for("index"))


# PUBLIC LIST


@app.route("/list", defaults={"page": 1}, methods=["GET"])  # type: ignore
@app.route("/list/<int:page>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
def show_list(page: int = 1) -> Any:
    pw = request.args.get("pw", "")

    if not logged_in():
        if not config.list_enabled:
            return redirect(url_for("index"))

        if config.list_password and (pw != config.list_password):
            return redirect(url_for("index"))

    page_size = request.args.get("page_size", config.list_page_size)

    files, total, next_page = procs.get_files(
        page, page_size, max_files=config.list_max_files
    )

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
    )
