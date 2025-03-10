from __future__ import annotations

# Standard
from typing import Any, Never
from functools import wraps
from typing import Callable
from datetime import timedelta
from pathlib import Path

# Libraries
from flask import Flask, render_template, request, send_file, jsonify  # type: ignore
from flask import redirect, url_for, session, abort  # pyright: ignore
from flask_cors import CORS  # type: ignore
from flask_limiter import Limiter  # type: ignore
from flask_limiter.util import get_remote_address  # type: ignore

# Modules
import utils
import upload_procs
import post_procs
import user_procs
import react_procs
import database
from config import config
from post_procs import Post
from user_procs import User
from react_procs import Reaction

# Possible exit here
database.check_db()

app = Flask(__name__)
app.url_map.strict_slashes = False
app.secret_key = config.app_key
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=config.session_days)

# Enable all cross origin requests
CORS(app)


def get_user_id() -> int | None:
    uid = session.get("user_id")

    if uid:
        return int(uid)

    return None


def get_user() -> User | None:
    user_id = get_user_id()

    if not user_id:
        return None

    return user_procs.get_user(user_id)


def logged_in() -> bool:
    return bool(get_user_id())


def can_read(user: User | None = None) -> bool:
    if not user:
        user = get_user()

    if not user:
        return False

    return user.admin or user.reader


def list_visible(user: User | None = None) -> bool:
    return config.list_enabled and ((not config.list_private) or can_read(user))


def login_required(f: Any) -> Any:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not logged_in():
            return redirect(url_for("login"))

        user = get_user()

        if not user:
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f: Any) -> Any:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not logged_in():
            return redirect(url_for("login"))

        user = get_user()

        if (not user) or (not user.admin):
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


def reader_required(f: Any) -> Any:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        user = get_user()

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
    return render_template("over.jinja")


def fill_session(user: User) -> None:
    session["user_id"] = user.id
    session.permanent = True


def common_configs(user: User | None = None) -> dict[str, Any]:
    return {
        "is_user": bool(user),
        "is_admin": user.admin if user else False,
        "user_id": user.id if user else 0,
        "username": user.username if user else "",
        "user_name": user.name if user else "",
        "reader": (not config.list_private)
        or ((user.admin or user.reader) if user else False),
        "background_color": config.background_color,
        "accent_color": config.accent_color,
        "font_color": config.font_color,
        "text_color": config.text_color,
        "link_color": config.link_color,
        "alt_color": config.alt_color,
        "font_family": config.font_family,
        "font_size": config.font_size,
        "admin_font_size": config.admin_font_size,
        "links": config.links,
        "file_path": config.file_path,
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
    user = get_user()

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

    banner = utils.get_banner()

    return render_template(
        "index.jinja",
        mode="index",
        max_size=max_size,
        max_size_str=max_size_str,
        show_max_size=config.show_max_size,
        show_image=config.show_image,
        main_title=config.main_title,
        image_tooltip=config.image_tooltip,
        max_title_length=config.max_title_length,
        allow_titles=config.allow_titles,
        show_list=show_list,
        show_admin=user and user.admin,
        description=config.description_index,
        upload_enabled=config.web_uploads_enabled,
        max_name_length=config.max_user_name_length,
        max_password_length=config.max_user_password_length,
        max_upload_files=config.max_upload_files,
        show_compress=config.show_compress,
        banner=banner,
        **common_configs(user),
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
        "message.jinja",
        mode=data["mode"],
        message=data["message"],
        **common_configs(),
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

    post = post_procs.get_post(name=name, full=True, increase=True, full_reactions=True)

    if not post:
        return over()

    if user:
        owned = user.admin or ((post.username == user.username) and config.allow_edit)
    else:
        owned = False

    show_list = list_visible(user)
    can_react = False

    if len(post.reactions) < config.post_reaction_limit:
        if config.reactions_enabled:
            if user:
                can_react = user.reacter

    return render_template(
        "post.jinja",
        mode="post",
        post=post,
        owned=owned,
        description=config.description_post,
        reactions_enabled=config.reactions_enabled,
        text_reaction_length=config.text_reaction_length,
        post_refresh_interval=config.post_refresh_interval,
        post_refresh_times=config.post_refresh_times,
        max_post_name_length=config.max_post_name_length,
        max_reaction_name_length=config.max_reaction_name_length,
        can_react=can_react,
        show_list=show_list,
        **common_configs(user),
    )


@app.route("/refresh", methods=["POST"])  # type: ignore
@payload_check()
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
def refresh() -> Any:
    data = request.get_json()
    post_id = data.get("post_id", None)

    if not post_id:
        return error_json

    ok, update = post_procs.get_post_update(post_id)

    if not ok:
        return error_json

    return {"update": update}, 200


@app.route("/next/<string:current>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@reader_required
def next_post(current: str) -> Any:
    post = post_procs.get_next_post(current)

    if not post:
        return over()

    return redirect(url_for("post", name=post.name))


@app.route("/random", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@reader_required
def random_post() -> Any:
    used_ids = session["used_ids"] if "used_ids" in session else []
    post = post_procs.get_random_post(used_ids)

    if post:
        used_ids.append(post.id)
        session["used_ids"] = used_ids
        return redirect(url_for("post", name=post.name))

    return over()


# FILES


@app.route(f"/{config.file_path}/<path:name>", methods=["GET"])  # type: ignore
@app.route(f"/{config.file_path}/<path:name>/<path:original>", methods=["GET"])  # type: ignore
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

    post = post_procs.get_post(name=name, full=False, increase=True)

    if not post:
        return over()

    rootdir = utils.files_dir()
    return send_file(
        rootdir / post.full, download_name=original, max_age=config.max_age
    )


@app.route("/sample/<path:name>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
def get_sample(name: str) -> Any:
    if not config.allow_hotlinks:
        referrer = request.referrer
        host = request.host_url

        if (not referrer) or (not referrer.startswith(host)):
            abort(403)

    file = post_procs.get_sample(name)

    if not file:
        return over()

    rootdir = utils.samples_dir()
    return send_file(rootdir / file, max_age=config.max_age)


@app.route("/get_sample", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
def get_sample_2() -> Any:
    data = request.get_json()
    name = data.get("name", "")

    if not name:
        return error_json

    file = post_procs.get_sample(name)

    if not file:
        return error_json

    return jsonify(
        {
            "path": str(Path("/sample") / Path(file.stem)),
            "name": file.stem,
            "ext": file.suffix[1:],
        }
    )


# ADMIN


@app.route("/admin/<string:what>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@admin_required
def admin(what: str) -> Any:
    if what not in ["posts", "users", "reactions"]:
        return redirect(url_for("index"))

    user = get_user()

    if not user:
        return over()

    query = request.args.get("query", "")
    def_date = "register_date" if what == "users" else "date"
    sort = request.args.get("sort", def_date)
    user_id = int(request.args.get("user_id", 0))
    media_type = request.args.get("media_type", None)
    page = int(request.args.get("page", 1))
    page_size = str(request.args.get("page_size", config.admin_page_size))
    post_items: list[Post] = []
    user_items: list[User] = []
    reaction_items: list[Reaction] = []

    if what == "posts":
        post_items, total, next_page = post_procs.get_posts(
            page,
            page_size,
            query=query,
            sort=sort,
            user_id=user_id,
            media_type=media_type,
            admin=True,
        )
    elif what == "users":
        user_items, total, next_page = user_procs.get_users(
            page,
            page_size,
            query=query,
            sort=sort,
            user_id=user_id,
            admin=True,
        )
    elif what == "reactions":
        reaction_items, total, next_page = react_procs.get_reactions(
            page,
            page_size,
            query=query,
            sort=sort,
            admin=True,
            user_id=user_id,
        )
    else:
        return over()

    def_page_size = page_size == str(config.admin_page_size)
    html_page = f"admin_{what}.jinja"

    if what == "posts":
        title = "Posts Admin"
    elif what == "reactions":
        title = "Reactions Admin"
    elif what == "users":
        title = "Users Admin"
    else:
        return over()

    items: list[Post] | list[User] | list[Reaction]
    mode = f"admin_{what}"

    if what == "posts":
        items = post_items
    elif what == "users":
        items = user_items
    elif what == "reactions":
        items = reaction_items

    return render_template(
        html_page,
        mode=mode,
        items=items,
        total=total,
        page=page,
        title=title,
        next_page=next_page,
        page_size=page_size,
        media_type=media_type,
        def_page_size=def_page_size,
        max_title_length=config.max_title_length,
        used_user_id=user_id,
        sort=sort,
        **common_configs(user),
    )


# FILES


@app.route("/delete_posts", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@admin_required
def delete_posts() -> Any:
    data = request.get_json()
    ids = data.get("ids", None)
    return post_procs.delete_posts(ids)


@app.route("/delete_all_posts", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(5))  # type: ignore
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
    post_id = data.get("post_id", None)
    user = get_user()

    if not user:
        return error_json

    return post_procs.delete_post(post_id, user=user)


@app.route("/edit_title", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@login_required
def edit_title() -> Any:
    data = request.get_json()
    post_id = data.get("post_id", None)
    title = data.get("title", None)
    user = get_user()

    if not user:
        return error_json

    return post_procs.edit_post_title(post_id, title, user=user)


# AUTH


@app.route("/login", methods=["GET", "POST"])  # type: ignore
@limiter.limit(rate_limit(6))  # type: ignore
@payload_check()
def login() -> Any:
    message = ""

    if request.method == "POST":
        ok, message, user = user_procs.login(request)

        if ok and user:
            fill_session(user)
            return redirect(url_for("index"))

    return render_template(
        "login.jinja",
        message=message,
        **common_configs(),
    )


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
            fill_session(user)
            return redirect(url_for("index"))

    return render_template(
        "register.jinja",
        message=message,
        **common_configs(),
    )


@app.route("/logout", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(5))  # type: ignore
@payload_check()
def logout() -> Any:
    session.clear()
    return redirect(url_for("index"))


# LIST


@app.route("/list/<string:what>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
def show_list(what: str) -> Any:
    user = get_user()

    if not user:
        return over()

    admin = user.admin
    user_id = int(request.args.get("user_id", 0))
    history = user.id == user_id

    if not history:
        if not config.list_enabled and (not admin):
            return redirect(url_for("index"))

        if config.list_private and (not admin):
            if not logged_in():
                return redirect(url_for("login"))

            if not user.reader:
                return redirect(url_for("index"))

    page = int(request.args.get("page", 1))
    page_size = str(request.args.get("page_size", config.list_page_size))
    sort = request.args.get("sort", "date")
    query = request.args.get("query", "")
    media_type = request.args.get("media_type", None)
    only_listed = not history
    post_items: list[Post] = []
    reaction_items: list[Reaction] = []

    if what == "posts":
        post_items, total, next_page = post_procs.get_posts(
            page,
            page_size,
            max_posts=config.list_max_posts,
            sort=sort,
            query=query,
            user_id=user_id,
            only_listed=only_listed,
            media_type=media_type,
            admin=False,
        )
    elif what == "reactions":
        reaction_items, total, next_page = react_procs.get_reactions(
            page,
            page_size,
            max_reactions=config.list_max_reactions,
            only_listed=only_listed,
            user_id=user_id,
            query=query,
            sort=sort,
            admin=True,
        )
    else:
        return over()

    def_page_size = page_size == str(config.list_page_size)
    html_page = f"admin_{what}.jinja"

    if what == "posts":
        title = "List Posts" if not history else "Post History"
    elif what == "reactions":
        title = "List Reactions" if not history else "Reaction History"
    else:
        return over()

    items: list[Post] | list[Reaction]
    mode = f"list_{what}"

    if what == "posts":
        items = post_items
    elif what == "reactions":
        items = reaction_items

    return render_template(
        html_page,
        mode=mode,
        items=items,
        total=total,
        page=page,
        title=title,
        next_page=next_page,
        page_size=page_size,
        media_type=media_type,
        def_page_size=def_page_size,
        max_title_length=config.max_title_length,
        used_user_id=user_id,
        sort=sort,
        back="/",
        **common_configs(user),
    )


@app.route("/fresh", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@reader_required
def latest_post() -> Any:
    post = post_procs.get_latest_post()

    if not post:
        return over()

    return redirect(url_for("post", name=post.name))


# USERS


@app.route("/edit_user", defaults={"user_id": 0}, methods=["GET", "POST"])  # type: ignore
@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@admin_required
def edit_user(user_id: int = 0) -> Any:
    if user_id:
        mode = "edit"
    else:
        mode = "add"

    def show_edit(message: str = "") -> Any:
        user = user_procs.get_user(user_id)

        if (not user) and mode == "edit":
            return redirect(url_for("admin", what="users"))

        if user and (mode == "edit"):
            title = f"Edit: {user.username}"
        else:
            title = "Add User"

        if message:
            title = f"{title} ({message})"

        return render_template(
            "edit_user.jinja",
            user=user or {},
            title=title,
            mode=mode,
            **common_configs(),
        )

    user = get_user()

    if not user:
        return redirect(url_for("admin", what="users"))

    if request.method == "POST":
        ok, msg, uid = user_procs.edit_user(mode, request, user, user_id)

        if ok:
            if mode == "add":
                return redirect(url_for("edit_user", user_id=uid))

            return show_edit("Updated")

        return show_edit(msg)

    return show_edit()


@app.route("/delete_users", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@admin_required
def delete_users() -> Any:
    data = request.get_json()
    ids = data.get("ids", None)

    if not ids:
        return error_json

    user = get_user()

    if not user:
        return error_json

    return user_procs.delete_users(ids, user.id)


@app.route("/delete_normal_users", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(5))  # type: ignore
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
    user_id = data.get("user_id", None)

    if not user_id:
        return error_json

    user = get_user()

    if not user:
        return error_json

    return user_procs.delete_user(user_id, user.id)


@app.route("/mod_user", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@login_required
def mod_user() -> Any:
    user = get_user()

    if not user:
        return error_json

    data = request.get_json()
    ids = data.get("ids", None)
    what = data.get("what", None)
    value = data.get("value", None)
    vtype = data.get("vtype", None)

    if (not ids) or (not what) or (value is None) or (not vtype):
        return error_json

    return user_procs.mod_user(ids, what, value, vtype, user)


# ICONS


@app.route("/get_icons", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@login_required
def get_icons() -> Any:
    return {"icons": utils.ICONS}


# REACTIONS


@app.route("/react", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check(max_post=9096)
@login_required
def add_reaction() -> Any:
    user = get_user()

    if not user:
        return error_json

    data = request.get_json()
    post_id = int(data.get("post_id", 0))
    text = str(data.get("text", ""))
    return react_procs.add_reaction(post_id, text, user)


@app.route("/delete_reactions", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@admin_required
def delete_reactions() -> Any:
    data = request.get_json()
    ids = data.get("ids", None)
    return react_procs.delete_reactions(ids)


@app.route("/delete_reaction", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@login_required
def delete_reaction() -> Any:
    user = get_user()

    if not user:
        return error_json

    data = request.get_json()
    id_ = data.get("id", None)
    return react_procs.delete_reaction(id_, user)


@app.route("/edit_reaction", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(config.rate_limit))  # type: ignore
@payload_check()
@login_required
def edit_reaction() -> Any:
    user = get_user()

    if not user:
        return error_json

    data = request.get_json()
    id_ = int(data.get("id", 0))

    if id_ <= 0:
        return error_json

    text = data.get("text", "")
    return react_procs.edit_reaction(id_, text, user)


@app.route("/delete_all_reactions", methods=["POST"])  # type: ignore
@limiter.limit(rate_limit(5))  # type: ignore
@payload_check()
@admin_required
def delete_all_reactions() -> Any:
    return react_procs.delete_all_reactions()
