from __future__ import annotations

# Standard
from typing import Any
from functools import wraps

# Libraries
from flask import Flask, render_template, request, send_file  # type: ignore
from flask import redirect, url_for, session, flash, abort  # pyright: ignore
from flask_cors import CORS  # type: ignore
from flask_simple_captcha import CAPTCHA  # type: ignore
from flask_limiter import Limiter  # type: ignore
from flask_limiter.util import get_remote_address  # type: ignore

# Modules
import utils
import procs
import post_procs
import user_procs
from config import config
from post_procs import Post
from user_procs import User


app = Flask(__name__)
app.url_map.strict_slashes = False
app.secret_key = config.app_key
app.config["MAX_CONTENT_LENGTH"] = config.max_size * 1_000_000

# Enable all cross origin requests
CORS(app)

simple_captcha = CAPTCHA(config=config.get_captcha())
app = simple_captcha.init_app(app)


def get_username() -> str:
    return str(session.get("username", ""))


def get_user() -> User | None:
    username = get_username()
    return user_procs.get_user(username)


def logged_in() -> bool:
    return bool(get_username())


def can_list(user: User | None = None) -> bool:
    if not user:
        user = user_procs.get_user(get_username())

    if not user:
        return False

    return user.admin or user.can_list


def list_visible(user: User | None = None) -> bool:
    return config.list_enabled and ((not config.list_private) or can_list(user))


def login_required(f: Any) -> Any:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not logged_in():
            return redirect(url_for("login"))

        user = user_procs.get_user(get_username())

        if not user:
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f: Any) -> Any:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not logged_in():
            return redirect(url_for("login"))

        user = user_procs.get_user(get_username())

        if (not user) or (not user.admin):
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


def list_required(f: Any) -> Any:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        user = user_procs.get_user(get_username())

        if not list_visible(user):
            return redirect(url_for("index"))

        return f(*args, **kwargs)

    return decorated_function


def rate_limit(n: int) -> str:
    return f"{n} per minute"


def over() -> Any:
    return render_template("over.html")


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

    user = get_user()
    admin = user and user.admin
    uname = user.username if user else ""
    is_user = bool(user)

    if (not user) and (not config.anon_uploads_enabled):
        return render_template("fallback.html")

    if request.method == "POST":
        try:
            ok, ans = procs.upload(request, username=uname)

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
            return over()

    if config.require_captcha and (not is_user):
        captcha = simple_captcha.create()
    else:
        captcha = None

    show_list = list_visible(user)
    show_history = admin or (config.history_enabled and is_user)

    if user:
        max_size = user.max_size

        if max_size <= 0:
            max_size = config.max_size_user
    else:
        max_size = config.max_size_anon

    max_size_str = max_size
    max_size *= 1_000_000

    return render_template(
        "index.html",
        captcha=captcha,
        image_name=procs.get_image_name(),
        max_size=max_size,
        max_size_str=max_size_str,
        show_max_size=config.show_max_size,
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
        is_user=is_user,
        show_history=show_history,
        show_list=show_list,
        show_admin=admin,
        description=config.description_index,
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


# POST


@app.route("/post/<string:name>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
def post(name: str) -> Any:
    user = get_user()

    if not config.public_posts:
        if not user:
            return over()

    post = post_procs.get_post(name)

    if not post:
        return over()

    if user:
        owned = user.admin or ((post.username == user.username) and config.allow_edit)
    else:
        owned = False

    show_list = list_visible(user)

    return render_template(
        "post.html",
        post=post,
        owned=owned,
        file_path=config.file_path,
        background_color=config.background_color,
        accent_color=config.accent_color,
        font_color=config.font_color,
        text_color=config.text_color,
        link_color=config.link_color,
        font_family=config.font_family,
        description=config.description_post,
        show_list=show_list,
    )


@app.route("/next/<string:current>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@list_required
def next_post(current: str) -> Any:
    name = post_procs.get_next_post(current)

    if not name:
        return redirect(url_for("post", name=current))

    return redirect(url_for("post", name=name))


@app.route("/random", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@list_required
def random_post() -> Any:
    used_names = session["used_names"] if "used_names" in session else []
    name = post_procs.get_random_post(used_names)

    if name:
        used_names.append(name)
        session["used_names"] = used_names
        return redirect(url_for("post", name=name))

    if used_names:
        first = used_names[0]
        used_names = [first]
        session["used_names"] = used_names
        return redirect(url_for("post", name=first))

    return over()


# FILE


@app.route(f"/{config.file_path}/<path:name>", methods=["GET"])  # type: ignore
@app.route(f"/{config.file_path}/<path:name>/<string:original>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
def get_file(name: str, original: str | None = None) -> Any:
    if not config.allow_hotlinks:
        referrer = request.referrer
        host = request.host_url

        if (not referrer) or (not referrer.startswith(host)):
            abort(403)

    if not config.public_posts:
        user = get_user()

        if not user:
            return over()

    post = post_procs.get_post(name)

    if not post:
        return over()

    fd = utils.files_dir()
    return send_file(fd / post.full, download_name=original, max_age=config.max_age)


# ADMIN


@app.route("/admin", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@admin_required
def admin_fallback() -> Any:
    return render_template("admin.html")


@app.route("/admin/<string:what>", defaults={"page": 1}, methods=["GET"])  # type: ignore
@app.route("/admin/<string:what>/<int:page>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@admin_required
def admin(what: str, page: int = 1) -> Any:
    if what not in ["posts", "users"]:
        return redirect(url_for("index"))

    query = request.args.get("query", "")
    def_date = "date" if what == "posts" else "register_date"
    sort = request.args.get("sort", def_date)
    page_size = request.args.get("page_size", config.admin_page_size)
    items: list[Post] | list[User]

    if what == "posts":
        items, total, next_page = post_procs.get_posts(
            page, page_size, query=query, sort=sort
        )
    else:
        items, total, next_page = user_procs.get_users(
            page, page_size, query=query, sort=sort
        )

    def_page_size = page_size == config.admin_page_size
    html_page = "posts.html" if what == "posts" else "users.html"

    return render_template(
        html_page,
        items=items,
        total=total,
        page=page,
        next_page=next_page,
        page_size=page_size,
        def_page_size=def_page_size,
        sort=sort,
    )


# FILES


@app.route("/delete_posts", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@admin_required
def delete_posts() -> Any:
    data = request.get_json()
    names = data.get("names", None)
    return post_procs.delete_posts(names)


@app.route("/delete_all_posts", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(2))  # type: ignore
@admin_required
def delete_all_posts() -> Any:
    return post_procs.delete_all_posts()


@app.route("/delete_post", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@login_required
def delete_post() -> Any:
    data = request.get_json()
    name = data.get("name", None)
    user = get_user()

    if not user:
        return over()

    return post_procs.delete_post(name, user=user)


@app.route("/edit_title", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@login_required
def edit_title() -> Any:
    data = request.get_json()
    name = data.get("name", None)
    title = data.get("title", None)
    user = get_user()

    if not user:
        return over()

    return post_procs.edit_post_title(name, title, user=user)


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

        user = user_procs.check_auth(username, password)

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
    user = get_user()
    admin = user and user.admin

    if not config.list_enabled and (not admin):
        return redirect(url_for("index"))

    if config.list_private and (not admin):
        if not logged_in():
            return redirect(url_for("login"))

        if not user:
            return redirect(url_for("login"))

        if not user.can_list:
            return redirect(url_for("index"))

    page_size = request.args.get("page_size", config.list_page_size)
    sort = request.args.get("sort", "date")
    query = request.args.get("query", "")

    posts, total, next_page = post_procs.get_posts(
        page,
        page_size,
        max_posts=config.list_max_posts,
        sort=sort,
        query=query,
        only_listed=True,
    )

    def_page_size = page_size == config.list_page_size

    return render_template(
        "list.html",
        mode="list",
        items=posts,
        total=total,
        page=page,
        next_page=next_page,
        page_size=page_size,
        def_page_size=def_page_size,
        sort=sort,
    )


# HISTORY


@app.route("/history", defaults={"page": 1}, methods=["GET"])  # type: ignore
@app.route("/history/<int:page>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@login_required
def show_history(page: int = 1) -> Any:
    user = get_user()

    if not user:
        return redirect(url_for("login"))

    admin = user and user.admin

    if not config.history_enabled and (not admin):
        return redirect(url_for("index"))

    page_size = request.args.get("page_size", config.list_page_size)
    username = user.username

    if not username:
        return redirect(url_for("index"))

    posts, total, next_page = post_procs.get_posts(
        page, page_size, max_posts=config.list_max_posts, username=username
    )

    def_page_size = page_size == config.list_page_size

    return render_template(
        "list.html",
        mode="history",
        items=posts,
        total=total,
        page=page,
        next_page=next_page,
        page_size=page_size,
        def_page_size=def_page_size,
    )


# USERS


@app.route("/edit_user", defaults={"username": ""}, methods=["GET", "POST"])  # type: ignore
@app.route("/edit_user/<string:username>", methods=["GET", "POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@admin_required
def edit_user(username: str = "") -> Any:
    if username:
        mode = "edit"
    else:
        mode = "add"

    def show_edit(message: str = "") -> Any:
        user = user_procs.get_user(username)

        if (not user) and mode == "edit":
            return redirect(url_for("admin", what="users"))

        if mode == "edit":
            title = "Edit User"
        else:
            title = "Add User"

        if message:
            title = f"{title} ({message})"

        return render_template(
            "edit_user.html",
            user=user or {},
            title=title,
        )

    user = get_user()

    if not user:
        return redirect(url_for("admin", what="users"))

    if request.method == "POST":
        uname = user_procs.edit_user(mode, request, username, user)

        if uname:
            if mode == "add":
                return redirect(url_for("edit_user", username=uname))

            return show_edit("Updated")

        return show_edit("Error")

    return show_edit()


@app.route("/delete_users", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@admin_required
def delete_users() -> Any:
    data = request.get_json()
    usernames = data.get("usernames", None)

    if not usernames:
        return {}, 400

    user = get_user()

    if not user:
        return over()

    return user_procs.delete_users(usernames, user.username)


@app.route("/delete_normal_users", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(2))  # type: ignore
@admin_required
def delete_normal_users() -> Any:
    return user_procs.delete_normal_users()


@app.route("/delete_user", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@admin_required
def delete_user() -> Any:
    data = request.get_json()
    username = data.get("username", None)

    if not username:
        return {}, 400

    user = get_user()

    if not user:
        return over()

    return user_procs.delete_user(username, user.username)


@app.route("/mod_user", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@admin_required
def mod_user() -> Any:
    data = request.get_json()
    usernames = data.get("usernames", None)
    what = data.get("what", None)
    value = data.get("value", None)
    vtype = data.get("vtype", None)

    if (not usernames) or (not what) or (value is None) or (not vtype):
        return {}, 400

    user = get_user()

    if not user:
        return {}, 400

    return user_procs.mod_user(usernames, what, value, vtype)
