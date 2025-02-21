from __future__ import annotations

# Standard
from typing import Any, Never
from functools import wraps
from typing import Callable

# Libraries
from flask import Flask, render_template, request, send_file  # type: ignore
from flask import redirect, url_for, session, abort  # pyright: ignore
from flask_cors import CORS  # type: ignore
from flask_limiter import Limiter  # type: ignore
from flask_limiter.util import get_remote_address  # type: ignore

# Modules
import utils
import upload_procs
import post_procs
import user_procs
from config import config
from post_procs import Post
from user_procs import User


app = Flask(__name__)
app.url_map.strict_slashes = False
app.secret_key = config.app_key

# Enable all cross origin requests
CORS(app)


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


def payload_check(max_post: int = 2048, max_get: int = 2048) -> Callable[[Any], Any]:
    def decorator(f: Any) -> Any:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            if request.method == "POST":
                post_size = request.content_length or 0

                if post_size > max_post:
                    return "POST too big", 413
            elif request.method == "GET":
                get_size = len(request.url)

                if get_size > max_get:
                    return "GET too big", 414

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def rate_limit(n: int) -> str:
    return f"{n} per minute"


def over() -> Any:
    return render_template("over.html")


def theme_configs() -> dict[str, Any]:
    return {
        "background_color": config.background_color,
        "accent_color": config.accent_color,
        "font_color": config.font_color,
        "text_color": config.text_color,
        "link_color": config.link_color,
        "font_family": config.font_family,
        "font_size": config.font_size,
        "admin_font_size": config.admin_font_size,
    }


limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[rate_limit(config.rate_limit)],
    storage_uri=f"redis://localhost:{config.redis_port}",
    strategy="fixed-window",
)

error_json: tuple[dict[Never, Never], int] = {}, 400
invalid = "Error: Invalid request"
text_mtype = "text/plain"


# INDEX / UPLOAD


@app.route("/", methods=["POST", "GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
def index() -> Any:
    if not config.web_uploads_enabled:
        return render_template("fallback.html")

    user = get_user()
    is_user = bool(user)
    admin = user and user.admin

    if request.method == "POST":
        if not user:
            return over()

        try:
            ok, ans = upload_procs.upload(request, user)

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

    show_list = list_visible(user)

    if not user:
        max_size = 0
        max_size_str = 0
    else:
        max_size = user.max_size

        if max_size <= 0:
            max_size = config.max_size_user

        max_size_str = max_size
        max_size *= 1_000_000

    return render_template(
        "index.html",
        image_name=utils.get_image_name(),
        max_size=max_size,
        max_size_str=max_size_str,
        show_max_size=config.show_max_size,
        show_image=config.show_image,
        main_title=config.main_title,
        image_tooltip=config.image_tooltip,
        max_title_length=config.max_title_length,
        allow_titles=config.allow_titles,
        links=config.links,
        show_list=show_list,
        show_admin=admin,
        description=config.description_index,
        is_user=is_user,
        **theme_configs(),
    )


@app.route(f"/{config.api_upload_endpoint}", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
def api_upload() -> Any:
    if not config.api_upload_enabled:
        return "error"

    _, msg = upload_procs.api_upload(request)
    return msg


@app.route("/message", methods=["GET"])  # type: ignore
@payload_check()
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

    return render_template(
        "message.html",
        mode=data["mode"],
        message=data["message"],
        **theme_configs(),
    )


# POST


@app.route("/post/<string:name>", methods=["GET"])  # type: ignore
@payload_check()
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
def post(name: str) -> Any:
    user = get_user()

    if not config.public_posts:
        if not user:
            return over()

    post = post_procs.get_post(name, full=True, increase=True)

    if not post:
        return over()

    if user:
        owned = user.admin or ((post.username == user.username) and config.allow_edit)
    else:
        owned = False

    show_list = list_visible(user)
    can_react = False

    if len(post.reactions) < config.max_reactions_length:
        if config.reactions_enabled:
            if user:
                can_react = user.reacter

    return render_template(
        "post.html",
        post=post,
        owned=owned,
        file_path=config.file_path,
        description=config.description_post,
        reactions_enabled=config.reactions_enabled,
        character_reaction_length=config.character_reaction_length,
        post_refresh_interval=config.post_refresh_interval,
        post_refresh_times=config.post_refresh_times,
        can_react=can_react,
        show_list=show_list,
        **theme_configs(),
    )


@app.route("/refresh", methods=["POST"])  # type: ignore
@payload_check()
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
def refresh() -> Any:
    data = request.get_json()
    name = data.get("name", None)

    if not name:
        return error_json

    ok, update = post_procs.get_post_update(name)

    if not ok:
        return error_json

    return {"update": update}, 200


@app.route("/next/<string:current>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@list_required
def next_post(current: str) -> Any:
    name = post_procs.get_next_post(current)

    if not name:
        return redirect(url_for("post", name=current))

    return redirect(url_for("post", name=name))


@app.route("/random", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
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
@payload_check()
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

    post = post_procs.get_post(name, full=False, increase=True)

    if not post:
        return over()

    fd = utils.files_dir()
    return send_file(fd / post.full, download_name=original, max_age=config.max_age)


# ADMIN


@app.route("/admin", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@admin_required
def admin_fallback() -> Any:
    return render_template("admin.html", **theme_configs())


@app.route("/admin/<string:what>", defaults={"page": 1}, methods=["GET"])  # type: ignore
@app.route("/admin/<string:what>/<int:page>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@admin_required
def admin(what: str, page: int = 1) -> Any:
    if what not in ["posts", "users"]:
        return redirect(url_for("index"))

    query = request.args.get("query", "")
    def_date = "date" if what == "posts" else "register_date"
    sort = request.args.get("sort", def_date)
    username = request.args.get("username", "")
    page_size = request.args.get("page_size", config.admin_page_size)
    items: list[Post] | list[User]

    if what == "posts":
        items, total, next_page = post_procs.get_posts(
            page,
            page_size,
            query=query,
            sort=sort,
            username=username,
        )
    else:
        items, total, next_page = user_procs.get_users(
            page, page_size, query=query, sort=sort
        )

    def_page_size = page_size == config.admin_page_size
    html_page = "posts.html" if what == "posts" else "users.html"
    mode = "posts" if what == "posts" else "users"
    title = "Posts" if what == "posts" else "Users"

    return render_template(
        html_page,
        mode=mode,
        items=items,
        total=total,
        page=page,
        title=title,
        next_page=next_page,
        page_size=page_size,
        def_page_size=def_page_size,
        username=username,
        sort=sort,
        **theme_configs(),
    )


# FILES


@app.route("/delete_posts", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@admin_required
def delete_posts() -> Any:
    data = request.get_json()
    names = data.get("names", None)
    return post_procs.delete_posts(names)


@app.route("/delete_all_posts", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(2))  # type: ignore
@payload_check()
@admin_required
def delete_all_posts() -> Any:
    return post_procs.delete_all_posts()


@app.route("/delete_post", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
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
@payload_check()
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
@limiter.limit(rate_limit(6))  # type: ignore
@payload_check()
def login() -> Any:
    message = ""

    if request.method == "POST":
        ok, message, user = user_procs.login(request)

        if ok and user:
            session["username"] = user.username
            session["admin"] = user.admin
            return redirect(url_for("index"))

    return render_template("login.html", message=message)


@app.route("/register", methods=["GET", "POST"])  # type: ignore
@limiter.limit(rate_limit(6))  # type: ignore
@payload_check()
def register() -> Any:
    if not config.register_enabled:
        return over()

    message = ""

    if request.method == "POST":
        ok, message, user = user_procs.register(request)

        if ok and user:
            session["username"] = user.username
            session["admin"] = user.admin
            return redirect(url_for("index"))

    return render_template("register.html", message=message)


@app.route("/logout", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(3))  # type: ignore
@payload_check()
def logout() -> Any:
    session.pop("username", None)
    return redirect(url_for("index"))


# LIST


@app.route("/list", defaults={"page": 1}, methods=["GET"])  # type: ignore
@app.route("/list/<int:page>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@list_required
def show_list(page: int = 1) -> Any:
    user = get_user()

    if not user:
        return over()

    admin = user.admin
    username = request.args.get("username", "")
    history = user.username == username

    if not history:
        if not config.list_enabled and (not admin):
            return redirect(url_for("index"))

        if config.list_private and (not admin):
            if not logged_in():
                return redirect(url_for("login"))

            if not user.can_list:
                return redirect(url_for("index"))

    page = int(request.args.get("page", 1))
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
        username=username,
    )

    def_page_size = page_size == config.list_page_size
    title = "List" if not history else "History"

    return render_template(
        "posts.html",
        mode="list",
        items=posts,
        total=total,
        page=page,
        title=title,
        next_page=next_page,
        page_size=page_size,
        def_page_size=def_page_size,
        username=username,
        sort=sort,
        back="/",
        **theme_configs(),
    )


@app.route("/fresh", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@list_required
def latest_post() -> Any:
    post = post_procs.get_latest_post()

    if not post:
        return over()

    return redirect(url_for("post", name=post.name))


# USERS


@app.route("/edit_user", defaults={"username": ""}, methods=["GET", "POST"])  # type: ignore
@app.route("/edit_user/<string:username>", methods=["GET", "POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
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

        if user and (mode == "edit"):
            title = f"Edit: {user.username}"
        else:
            title = "Add User"

        if message:
            title = f"{title} ({message})"

        uname = user.username if user else ""

        return render_template(
            "edit_user.html",
            user=user or {},
            username=uname,
            title=title,
            mode=mode,
            **theme_configs(),
        )

    user = get_user()

    if not user:
        return redirect(url_for("admin", what="users"))

    if request.method == "POST":
        ok, value = user_procs.edit_user(mode, request, username, user)

        if ok:
            if mode == "add":
                return redirect(url_for("edit_user", username=value))

            return show_edit("Updated")

        return show_edit(value)

    return show_edit()


@app.route("/user_edit", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@login_required
def user_edit() -> Any:
    user = get_user()

    if not user:
        return over()

    data = request.get_json()
    what = data.get("what", None)
    value = data.get("value", None)

    if what not in ["name", "password"]:
        return over()

    if not getattr(config, f"allow_{what}_edit"):
        return over()

    return user_procs.user_edit(user, what, value)


@app.route("/delete_users", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@admin_required
def delete_users() -> Any:
    data = request.get_json()
    usernames = data.get("usernames", None)

    if not usernames:
        return error_json

    user = get_user()

    if not user:
        return over()

    return user_procs.delete_users(usernames, user.username)


@app.route("/delete_normal_users", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(2))  # type: ignore
@payload_check()
@admin_required
def delete_normal_users() -> Any:
    return user_procs.delete_normal_users()


@app.route("/delete_user", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@admin_required
def delete_user() -> Any:
    data = request.get_json()
    username = data.get("username", None)

    if not username:
        return error_json

    user = get_user()

    if not user:
        return over()

    return user_procs.delete_user(username, user.username)


@app.route("/mod_user", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@admin_required
def mod_user() -> Any:
    data = request.get_json()
    usernames = data.get("usernames", None)
    what = data.get("what", None)
    value = data.get("value", None)
    vtype = data.get("vtype", None)

    if (not usernames) or (not what) or (value is None) or (not vtype):
        return error_json

    user = get_user()

    if not user:
        return error_json

    return user_procs.mod_user(usernames, what, value, vtype)


# ICONS


@app.route("/get_icons", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@login_required
def get_icons() -> Any:
    return {"icons": utils.ICONS}


@app.route("/react", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@login_required
def react() -> Any:
    user = get_user()

    if not user:
        return over()

    data = request.get_json()
    name = data.get("name", None)
    text = data.get("text", None)
    mode = data.get("mode", None)

    return post_procs.react(name, text, user, mode)


# YOU


@app.route("/you", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@login_required
def you() -> Any:
    user = get_user()

    if not user:
        return over()

    allow_edit = config.allow_name_edit or config.allow_password_edit

    return render_template(
        "you.html",
        user=user,
        allow_edit=allow_edit,
        allow_name_edit=config.allow_name_edit,
        allow_password_edit=config.allow_password_edit,
        **theme_configs(),
    )
