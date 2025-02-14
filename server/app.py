from __future__ import annotations

# Standard
from typing import Any
from functools import wraps

# Libraries
from flask import Flask, render_template, request, Response, send_file  # type: ignore
from flask import redirect, url_for, session, flash, abort  # pyright: ignore
from flask_cors import CORS  # type: ignore
from flask_simple_captcha import CAPTCHA  # type: ignore
from flask_limiter import Limiter  # type: ignore
from flask_limiter.util import get_remote_address  # type: ignore

# Modules
import procs
import user_procs
import utils
from config import config


app = Flask(__name__)
app.url_map.strict_slashes = False
app.secret_key = config.app_key
app.config["MAX_CONTENT_LENGTH"] = config.get_max_file_size()
user_procs.update_userlist()

# Enable all cross origin requests
CORS(app)

simple_captcha = CAPTCHA(config=config.get_captcha())
app = simple_captcha.init_app(app)


def get_username() -> str:
    return str(session.get("username", ""))


def logged_in() -> bool:
    return bool(get_username())


def is_admin() -> bool:
    user = config.get_user(get_username())

    if not user:
        return False

    return user.admin


def can_list() -> bool:
    user = config.get_user(get_username())

    if not user:
        return False

    return user.admin or user.can_list


def login_required(f: Any) -> Any:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not logged_in():
            return redirect(url_for("login"))

        user = config.get_user(get_username())

        if not user:
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f: Any) -> Any:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not logged_in():
            return redirect(url_for("login"))

        user = config.get_user(get_username())

        if (not user) or (not user.admin):
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

    admin = is_admin()
    logged = logged_in()
    username = get_username()

    if request.method == "POST":
        try:
            ok, ans = procs.upload(request, username=username)

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

    if config.require_captcha and (not logged):
        captcha = simple_captcha.create()
    else:
        captcha = None

    show_list = False

    if (config.list_enabled and (not config.list_private)) or can_list():
        show_list = True

    show_history = admin or (config.history_enabled and logged)

    return render_template(
        "index.html",
        captcha=captcha,
        image_name=procs.get_image_name(),
        max_size=config.get_max_file_size(),
        max_file_size=config.max_file_size,
        show_max_file_size=config.show_max_file_size,
        show_image=config.show_image,
        background_color=config.background_color,
        accent_color=config.accent_color,
        font_color=config.font_color,
        text_color=config.text_color,
        link_color=config.link_color,
        font_family=config.font_family,
        main_title=config.main_title,
        image_tooltip=config.image_tooltip,
        max_title_length=config.max_title_length,
        allow_titles=config.allow_titles,
        links=config.links,
        is_user=logged,
        show_history=show_history,
        show_list=show_list,
        show_admin=admin,
        logged_in=logged,
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

    owned = is_admin() or ((file.username == get_username()) and config.allow_edit)

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
        owned=owned,
    )


@app.route(f"/{config.file_path}/<path:name>", methods=["GET"])  # type: ignore
@app.route(f"/{config.file_path}/<path:name>/<string:original>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
def get_file(name: str, original: str | None = None) -> Any:
    if not config.allow_hotlinks:
        referrer = request.referrer
        host = request.host_url

        if (not referrer) or (not referrer.startswith(host)):
            abort(403)

    file = procs.get_file(name)

    if not file:
        return Response(invalid, mimetype=text_mtype)

    fd = utils.files_dir()
    return send_file(fd / file.full, download_name=original, max_age=config.max_age)


# ADMIN


@app.route("/admin", defaults={"page": 1}, methods=["GET"])  # type: ignore
@app.route("/admin/<int:page>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@admin_required
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
@admin_required
def delete_files() -> Any:
    data = request.get_json()
    files = data.get("files", None)
    return procs.delete_files(files)


@app.route("/delete_all_files", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(2))  # type: ignore
@admin_required
def delete_all() -> Any:
    return procs.delete_all()


@app.route("/delete_file", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@login_required
def delete_file() -> Any:
    data = request.get_json()
    file = data.get("file", None)
    return procs.delete_file(file, get_username(), is_admin())


@app.route("/edit_title", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@login_required
def edit_title() -> Any:
    data = request.get_json()
    name = data.get("name", None)
    title = data.get("title", None)
    return procs.edit_title(name, title, get_username(), is_admin())


# AUTH


@app.route("/login", methods=["GET", "POST"])  # type: ignore
@limiter.limit(rate_limit(5))  # type: ignore
def login() -> Any:
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if (not username) or (not password):
            flash("Invalid credentials")
            return redirect(url_for("login"))

        user = config.check_user(username, password)

        if user:
            session["username"] = user.username
            session["admin"] = user.admin
            return redirect(url_for("index"))

        flash("Invalid credentials")

    return render_template("login.html")


@app.route("/logout", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(3))  # type: ignore
def logout() -> Any:
    session.pop("username", None)
    return redirect(url_for("index"))


# LIST


@app.route("/list", defaults={"page": 1}, methods=["GET"])  # type: ignore
@app.route("/list/<int:page>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
def show_list(page: int = 1) -> Any:
    admin = is_admin()

    if not config.list_enabled and (not admin):
        return redirect(url_for("index"))

    if config.list_private and (not admin):
        if not logged_in():
            return redirect(url_for("login"))

        user = config.get_user(get_username())

        if not user:
            return redirect(url_for("login"))

        if not user.can_list:
            return redirect(url_for("index"))

    page_size = request.args.get("page_size", config.list_page_size)

    files, total, next_page = procs.get_files(
        page, page_size, max_files=config.list_max_files
    )

    def_page_size = page_size == config.list_page_size

    return render_template(
        "list.html",
        mode="list",
        files=files,
        total=total,
        page=page,
        next_page=next_page,
        page_size=page_size,
        def_page_size=def_page_size,
    )


# HISTORY


@app.route("/history", defaults={"page": 1}, methods=["GET"])  # type: ignore
@app.route("/history/<int:page>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@login_required
def show_history(page: int = 1) -> Any:
    admin = is_admin()

    if not config.history_enabled and (not admin):
        return redirect(url_for("index"))

    page_size = request.args.get("page_size", config.list_page_size)
    username = get_username()

    if not username:
        return redirect(url_for("index"))

    files, total, next_page = procs.get_files(
        page, page_size, max_files=config.list_max_files, username=username
    )

    def_page_size = page_size == config.list_page_size

    return render_template(
        "list.html",
        mode="history",
        files=files,
        total=total,
        page=page,
        next_page=next_page,
        page_size=page_size,
        def_page_size=def_page_size,
    )


# USERS


@app.route("/users", defaults={"page": 1}, methods=["GET"])  # type: ignore
@app.route("/users/<int:page>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@admin_required
def users(page: int = 1) -> Any:
    query = request.args.get("query", "")
    sort = request.args.get("sort", "date")
    page_size = request.args.get("page_size", config.admin_page_size)
    users, total, next_page = user_procs.get_users(page, page_size, query=query, sort=sort)
    def_page_size = page_size == config.admin_page_size

    return render_template(
        "users.html",
        users=users,
        total=total,
        page=page,
        next_page=next_page,
        page_size=page_size,
        def_page_size=def_page_size,
    )


@app.route("/edit_user", defaults={"username": ""}, methods=["GET", "POST"])  # type: ignore
@app.route("/edit_user/<string:username>", methods=["GET", "POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@admin_required
def edit_user(username: str = "") -> Any:
    if request.method == "POST":
        ok = user_procs.edit_user(request)

        if ok:
            return redirect(url_for("users"))
        else:
            return redirect(url_for("edit_user", username=username))
    else:
        if username:
            user = user_procs.get_user(username) or {}
        else:
            user = {}

        return render_template(
            "edit_user.html",
            user=user,
        )
