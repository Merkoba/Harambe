from __future__ import annotations

# Standard
import time
from dataclasses import dataclass
from collections import deque
from typing import Any

# Libraries
from flask import Request  # type: ignore
from werkzeug.security import generate_password_hash as hashpass  # type: ignore
from werkzeug.security import check_password_hash as checkpass  # pyright: ignore

# Modules
import utils
from config import config
import database
from database import User as DbUser


class UserData:
    def __init__(self, rpm: int) -> None:
        self.timestamps: deque[float] = deque()
        self.rpm = rpm
        self.window = 60

    def increment(self) -> None:
        now = time.time()
        self.timestamps.append(now)

        while self.timestamps and (self.timestamps[0] < (now - self.window)):
            self.timestamps.popleft()

    def blocked(self) -> bool:
        self.increment()
        return len(self.timestamps) > self.rpm


@dataclass
class User:
    id: int
    username: str
    password: str
    admin: bool
    name: str
    rpm: int
    max_size: int
    rpm_fill: int
    max_size_fill: int
    reader: bool
    mark: str
    register_date: int
    register_date_str: str
    last_date: int
    last_date_str: str
    admin_str: str
    reader_str: str
    lister: bool
    lister_str: str
    poster: bool
    reacter: bool
    mage: bool
    poster_str: str
    reacter_str: str
    mage_str: str
    num_posts: int
    num_reactions: int
    regdate_ago: str
    lastdate_ago: str


user_types = {
    "id": "int",
    "username": "string",
    "password": "string",
    "admin": "bool",
    "name": "string",
    "rpm": "int",
    "max_size": "int",
    "reader": "bool",
    "mark": "string",
    "register_date": "int",
    "last_date": "int",
    "lister": "bool",
    "posts": "int",
    "reactions": "int",
    "poster": "bool",
    "reacter": "bool",
    "mage": "bool",
}


user_data: dict[str, UserData] = {}


def make_user(user: DbUser, now: int) -> User:
    reg_date_str = utils.nice_date(user.register_date)
    last_date_str = utils.nice_date(user.last_date)
    admin_str = "Yes" if user.admin else "No"
    reader_str = "Yes" if user.reader else "No"
    rpm_fill = user.rpm or config.requests_per_minute
    max_size_fill = user.max_size or config.max_size_user
    lister_str = "Yes" if user.lister else "No"
    poster_str = "Yes" if user.poster else "No"
    reacter_str = "Yes" if user.reacter else "No"
    mage_str = "Yes" if user.mage else "No"
    num_posts = user.num_posts if user.num_posts else 0
    num_reactions = user.num_reactions if user.num_reactions else 0
    regdate_ago = utils.time_ago(user.register_date, now)
    lastdate_ago = utils.time_ago(user.last_date, now)
    name = user.name or "Anon"

    return User(
        user.id,
        user.username,
        user.password,
        user.admin,
        name,
        user.rpm,
        user.max_size,
        rpm_fill,
        max_size_fill,
        user.reader,
        user.mark,
        user.register_date,
        reg_date_str,
        user.last_date,
        last_date_str,
        admin_str,
        reader_str,
        user.lister,
        lister_str,
        user.poster,
        user.reacter,
        user.mage,
        poster_str,
        reacter_str,
        mage_str,
        num_posts,
        num_reactions,
        regdate_ago,
        lastdate_ago,
    )


def get_userlist(user_id: int | None = None) -> list[User]:
    now = utils.now()
    users = database.get_users(user_id=user_id)
    return [make_user(user, now) for user in users]


def get_users(
    page: int = 1,
    page_size: str = "default",
    query: str = "",
    sort: str = "register_date_desc",
    admin: bool = False,
    user_id: int | None = None,
    random: bool = False,
) -> tuple[list[User], str, bool]:
    psize = 0

    if page_size == "default":
        psize = config.admin_page_size
    elif page_size == "all":
        pass  # Don't slice later
    else:
        psize = int(page_size)

    users = []
    query = utils.decode(query)
    query = utils.clean_query(query)

    for user in get_userlist(user_id):
        props = [
            "username",
            "name",
            "max_size_fill",
            "register_date_str",
            "last_date_str",
            "regdate_ago",
            "lastdate_ago",
            "admin_str",
            "reacter_str",
            "mark",
            "rpm",
            "reader_str",
            "num_posts",
            "num_reactions",
        ]

        if not utils.do_query(user, query, props):
            continue

        users.append(user)

    total_str = f"{len(users)}"

    if random:
        utils.shuffle(users)
    else:
        utils.do_sort(users, sort, ["register_date", "last_date"])

    if psize > 0:
        start_index = (page - 1) * psize
        end_index = start_index + psize
        has_next_page = end_index < len(users)
        users = users[start_index:end_index]
    else:
        has_next_page = False

    return users, total_str, has_next_page


def get_user(user_id: int | None = None, username: str | None = None) -> User | None:
    if (not user_id) and (not username):
        return None

    users = database.get_users(user_id=user_id, username=username)
    user = users[0] if users else None

    if not user:
        return None

    return make_user(user, utils.now())


def check_value(user: User | None, what: str, value: Any) -> tuple[bool, Any]:
    vtype = user_types.get(what, None)

    if not vtype:
        return False, None

    if what == "username":
        value = value.strip()

        if not value:
            return False, None

        if not value.isalnum():
            return False, None

        if len(value) > config.max_user_username_length:
            return False, None
    elif what == "password":
        if value:
            if len(value) > config.max_user_password_length:
                return False, None

            value = hashpass(value)
        elif user and user.password:
            value = user.password
        else:
            return False, None
    elif what == "name":
        value = value.strip()

        if not value:
            if user and user.name:
                value = user.name

        if value:
            value = utils.single_line(value)

            if len(value) > config.max_user_name_length:
                return False, None
    elif what == "mark":
        value = value.strip()

        if not value:
            if user and user.mark:
                value = user.mark

        if value:
            if not value.isalnum():
                return False, None

            if len(value) > config.max_mark_length:
                return False, None
    elif value:
        if vtype == "int":
            try:
                value = min(9_000_000, max(0, int(value)))
            except ValueError:
                value = 0
        elif vtype == "string":
            value = "".join(
                [
                    c
                    for c in value
                    if c.isalnum() or c in [" ", "_", ".", ",", "-", "!", "?"]
                ]
            )

            value = utils.single_line(value)
            value = str(value)[:200]
        elif vtype == "bool":
            value = bool(value)

    return True, value


def edit_user(
    mode: str, request: Request, admin: User, user_id: int | None = None
) -> tuple[bool, str, int | None]:
    def error(msg: str) -> tuple[bool, str, None]:
        return False, msg, None

    if not request:
        return error("No Request")

    user = None

    if mode == "edit":
        user = get_user(user_id)

        if not user:
            return error("User not found")

    args = {}
    args["username"] = request.form.get("username")
    args["password"] = request.form.get("password")
    args["name"] = request.form.get("name")
    args["rpm"] = request.form.get("rpm")
    args["max_size"] = request.form.get("max_size")
    args["mark"] = request.form.get("mark")

    if request.form.get("reader") is None:
        args["reader"] = False
    else:
        args["reader"] = True

    if request.form.get("admin") is None:
        args["admin"] = False
    else:
        args["admin"] = True

    if request.form.get("lister") is None:
        args["lister"] = False
    else:
        args["lister"] = True

    if request.form.get("poster") is None:
        args["poster"] = False
    else:
        args["poster"] = True

    if request.form.get("reacter") is None:
        args["reacter"] = False
    else:
        args["reacter"] = True

    if request.form.get("mage") is None:
        args["mage"] = False
    else:
        args["mage"] = True

    if request.form.get("rpm") is None:
        args["rpm"] = 0

    if request.form.get("max_size") is None:
        args["max_size"] = 0

    if mode == "add":
        if database.username_exists(args["username"]):
            return error("Username already exists")
    elif mode == "edit":
        if not user:
            return error("User not found")

    n_args = {}

    for key in args:
        ok, value = check_value(user, key, args[key])

        if not ok:
            return error(f"Invalid Value '{key}'")

        n_args[key] = value

    if user and (user.id == admin.id):
        args["admin"] = True

    required = ["username", "password"]

    if not all(n_args.get(key) for key in required):
        return error("Missing Required")

    user_id = database.add_user(
        mode,
        n_args["username"],
        n_args["password"],
        n_args["admin"],
        n_args["name"],
        n_args["rpm"],
        n_args["max_size"],
        n_args["reader"],
        n_args["mark"],
        n_args["lister"],
        n_args["poster"],
        n_args["reacter"],
        n_args["mage"],
        user_id=user_id,
    )

    return True, "Ok", user_id


def check_auth(username: str, password: str) -> User | None:
    user = get_user(username=username)

    if not user:
        return None

    if user.username == username:
        if checkpass(user.password, password):
            return user

    return None


def delete_users(ids: list[int], admin_id: int) -> tuple[str, int]:
    if not ids:
        return utils.bad("Usernames were not provided")

    if admin_id in ids:
        return utils.bad("You can't delete yourself")

    for username in ids:
        do_delete_user(username)

    return utils.ok("User deleted successfully")


def delete_user(user_id: int, admin_id: int) -> tuple[str, int]:
    if not user_id:
        return utils.bad("User id was not provided")

    if user_id == admin_id:
        return utils.bad("You can't delete yourself")

    do_delete_user(user_id)
    return utils.ok("User deleted successfully")


def do_delete_user(user_id: int) -> None:
    if not user_id:
        return

    database.delete_user(user_id)


def delete_normal_users() -> tuple[str, int]:
    database.delete_normal_users()
    return utils.ok("Normal users deleted")


def check_user_limit(user: User) -> tuple[bool, str]:
    if user.username not in user_data:
        rpm = user.rpm or config.requests_per_minute
        user_data[user.username] = UserData(rpm)

    if user_data[user.username].blocked():
        return False, "Rate limit exceeded"

    return True, "ok"


def check_user_max(user: User, size: int) -> bool:
    megas = int(size / 1000 / 1000)

    if user.max_size > 0:
        return megas <= user.max_size

    return megas <= config.max_size_user


def mod_user(
    ids: list[int], what: str, value: str, vtype: str, user: User
) -> tuple[str, int]:
    if not what:
        return utils.bad("No field provided")

    if not user.admin:
        if (len(ids) != 1) or (ids[0] != user.id):
            return utils.bad("Forbidden")

    new_value: Any = None

    if vtype == "int":
        try:
            new_value = max(0, int(value))
        except ValueError:
            new_value = 0
    elif vtype == "string":
        new_value = str(value)
    elif vtype == "bool":
        new_value = bool(value)
    elif vtype == "number":
        new_value = int(value)

    if new_value is None:
        return utils.bad("Invalid value")

    if user.admin and (what == "admin"):
        if user.id in ids:
            ids.remove(user.id)

    ok, checked_value = check_value(None, what, new_value)

    if not ok:
        return utils.bad("Invalid value")

    if what == "username":
        if len(ids) != 1:
            return utils.bad("Only one user can be changed at a time")

        if database.username_exists(checked_value):
            return utils.bad("Username already exists")

    database.mod_user(ids, what, checked_value)
    return utils.ok()


def login(request: Request) -> tuple[bool, str, User | None]:
    if not request:
        return False, "No Request", None

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if (not username) or (not password):
        return False, "Missing details", None

    user = check_auth(username, password)

    if not user:
        return False, "Invalid username or password", None

    return True, "User logged in successfully", user


def register(request: Request) -> tuple[bool, str, User | None]:
    if not request:
        return False, "No Request", None

    now = utils.now()

    # Required
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    password_2 = request.form.get("password_2", "")

    if (not username) or (not password) or (not password_2):
        return False, "Missing details", None

    if password != password_2:
        return False, "Passwords do not match", None

    # Code
    if config.register_code:
        code = request.form.get("code", "")

        if code != config.register_code:
            return False, "Invalid code", None

    # Captcha
    if config.captcha_enabled:
        solution = request.form.get("solution", "")
        captcha_key = request.form.get("captcha_key", "")

        if not solution:
            return False, "Missing solution", None

        if not captcha_key:
            return False, "Missing captcha key", None

        try:
            solv = int(solution)
        except ValueError:
            return False, "Invalid solution", None

        captcha_value = utils.redis_get(captcha_key)

        if not captcha_value:
            return False, "Invalid captcha", None

        captcha_answer = captcha_value.get("answer", 0)
        captcha_time = captcha_value.get("time", 0)

        if (not captcha_answer) or (not captcha_time):
            return False, "Invalid captcha", None

        if (now - captcha_time) > config.max_captcha_time:
            return False, "Captcha expired", None

        if solv != captcha_answer:
            return False, "Invalid solution", None

        utils.redis_delete(captcha_key)

    # Username + Password
    ok, username = check_value(None, "username", username)

    if not ok:
        return False, "Invalid username", None

    ok, password = check_value(None, "password", password)

    if not ok:
        return False, "Invalid password", None

    if database.username_exists(username):
        return False, "User already exists", None

    # Name
    name = request.form.get("name", "").strip()

    if not name:
        name = username[0:12].strip()

    ok, name = check_value(None, "name", name)

    if not ok:
        return False, "Invalid name", None

    # Database
    user_id = database.add_user(
        "add", username=username, password=password, name=name, mage=config.default_mage
    )

    user = get_user(user_id)

    # Return
    if not user:
        return False, "User not found", None

    return True, "User registered successfully", user
