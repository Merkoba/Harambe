from __future__ import annotations

# Standard
import time
from dataclasses import dataclass
from collections import deque
from typing import Any

# Libraries
from flask import Request, jsonify  # type: ignore
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
    username: str
    password: str
    admin: bool
    name: str
    rpm: int
    max_size: int
    rpm_fill: int
    max_size_fill: int
    can_list: bool
    mark: str
    register_date: int
    register_date_str: str
    last_date: int
    last_date_str: str
    admin_str: str
    can_list_str: str
    lister: bool
    lister_str: str
    posts: int
    reacter: bool
    reacter_str: str


user_types = {
    "username": "string",
    "password": "string",
    "admin": "bool",
    "name": "string",
    "rpm": "int",
    "max_size": "int",
    "can_list": "bool",
    "mark": "string",
    "register_date": "int",
    "last_date": "int",
    "lister": "bool",
    "posts": "int",
    "reacter": "bool",
}


user_data: dict[str, UserData] = {}


def make_user(user: DbUser) -> User:
    reg_date_str = utils.nice_date(user.register_date)
    last_date_str = utils.nice_date(user.last_date)
    admin_str = "A: Yes" if user.admin else "A: No"
    can_list_str = "T: Yes" if user.can_list else "T: No"
    rpm_fill = user.rpm or config.requests_per_minute
    max_size_fill = user.max_size or config.max_size_user
    lister_str = "L: Yes" if user.lister else "R: No"
    reacter_str = "R: Yes" if user.reacter else "R: No"

    return User(
        user.username,
        user.password,
        user.admin,
        user.name,
        user.rpm,
        user.max_size,
        rpm_fill,
        max_size_fill,
        user.can_list,
        user.mark,
        user.register_date,
        reg_date_str,
        user.last_date,
        last_date_str,
        admin_str,
        can_list_str,
        user.lister,
        lister_str,
        user.posts,
        user.reacter,
        reacter_str,
    )


def get_userlist() -> list[User]:
    return [make_user(user) for user in database.get_users()]


def get_users(
    page: int = 1,
    page_size: str = "default",
    query: str = "",
    sort: str = "register_date",
) -> tuple[list[User], str, bool]:
    psize = 0

    if page_size == "default":
        psize = config.admin_page_size
    elif page_size == "all":
        pass  # Don't slice later
    else:
        psize = int(page_size)

    users = []
    query = utils.clean_query(query)

    for user in get_userlist():
        ok = (
            not query
            or query in utils.clean_query(user.username)
            or query in utils.clean_query(user.name)
            or query in utils.clean_query(user.max_size_fill)
            or query in utils.clean_query(user.register_date_str)
            or query in utils.clean_query(user.last_date_str)
            or query in utils.clean_query(user.admin_str)
            or query in utils.clean_query(user.reacter_str)
            or query in utils.clean_query(user.mark)
            or query in utils.clean_query(user.rpm)
            or query in utils.clean_query(user.can_list_str)
            or query in utils.clean_query(user.posts)
        )

        if not ok:
            continue

        users.append(user)

    total_str = f"{len(users)}"
    sort_users(users, sort)

    if psize > 0:
        start_index = (page - 1) * psize
        end_index = start_index + psize
        has_next_page = end_index < len(users)
        users = users[start_index:end_index]
    else:
        has_next_page = False

    return users, total_str, has_next_page


def sort_users(users: list[User], sort: str) -> None:
    if sort == "register_date":
        users.sort(key=lambda x: x.register_date, reverse=True)
    elif sort == "register_date_desc":
        users.sort(key=lambda x: x.register_date, reverse=False)

    elif sort == "last_date":
        users.sort(key=lambda x: x.last_date, reverse=True)
    elif sort == "last_date_desc":
        users.sort(key=lambda x: x.last_date, reverse=False)

    elif sort == "username":
        users.sort(key=lambda x: x.username, reverse=True)
    elif sort == "username_desc":
        users.sort(key=lambda x: x.username, reverse=False)

    elif sort == "name":
        users.sort(key=lambda x: x.name, reverse=True)
    elif sort == "name_desc":
        users.sort(key=lambda x: x.name, reverse=False)

    elif sort == "rpm":
        users.sort(key=lambda x: x.rpm, reverse=True)
    elif sort == "rpm_desc":
        users.sort(key=lambda x: x.rpm, reverse=False)

    elif sort == "max_size":
        users.sort(key=lambda x: x.max_size, reverse=True)
    elif sort == "max_size_desc":
        users.sort(key=lambda x: x.max_size, reverse=False)

    elif sort == "admin":
        users.sort(key=lambda x: x.admin, reverse=True)
    elif sort == "admin_desc":
        users.sort(key=lambda x: x.admin, reverse=False)

    elif sort == "can_list":
        users.sort(key=lambda x: x.can_list, reverse=True)
    elif sort == "can_list_desc":
        users.sort(key=lambda x: x.can_list, reverse=False)

    elif sort == "lister":
        users.sort(key=lambda x: x.lister, reverse=True)
    elif sort == "lister_desc":
        users.sort(key=lambda x: x.lister, reverse=False)

    elif sort == "posts":
        users.sort(key=lambda x: x.posts, reverse=True)
    elif sort == "posts_desc":
        users.sort(key=lambda x: x.posts, reverse=False)


def get_user(username: str) -> User | None:
    user = database.get_user(username)

    if not user:
        return None

    if user.username == username:
        return make_user(user)

    return None


def check_value(what: str, value: Any) -> tuple[bool, Any]:
    vtype = user_types.get(what, None)

    if not vtype:
        return False, None

    if what == "password":
        if value:
            value = hashpass(value)
        elif user and user.password:
            value = user.password
    elif value:
        if vtype == "int":
            try:
                value = min(max_num, max(0, int(value)))
            except ValueError:
                value = 0
        elif vtype == "string":
            value = "".join(
                [c for c in value if c.isalnum() or c in [" ", "_", ".", ",", "-"]]
            )

            value = utils.single_line(value)
            value = str(value)[:200]
        elif vtype == "bool":
            value = bool(value)

    return True, value


def edit_user(mode: str, request: Request, username: str, admin: User) -> str:
    if not request:
        return ""

    args = {}

    if mode == "add":
        args["username"] = request.form.get("username").lower()
    elif mode == "edit":
        args["username"] = username

    args["password"] = request.form.get("password")
    args["name"] = request.form.get("name")
    args["rpm"] = request.form.get("rpm")
    args["max_size"] = request.form.get("max_size")
    args["mark"] = request.form.get("mark")

    if request.form.get("can_list") is None:
        args["can_list"] = False
    else:
        args["can_list"] = True

    if request.form.get("admin") is None:
        args["admin"] = False
    else:
        args["admin"] = True

    if request.form.get("lister") is None:
        args["lister"] = False
    else:
        args["lister"] = True

    if request.form.get("rpm") is None:
        args["rpm"] = 0

    if request.form.get("max_size") is None:
        args["max_size"] = 0

    uname = args["username"]

    if not uname:
        return ""

    if not utils.is_valid_username(uname):
        return ""

    if uname == admin.username:
        args["admin"] = True

    user = get_user(uname)
    mode = "add" if user is None else "edit"
    max_num = 9_000_000
    n_args = {}

    for key in args:
        ok, value = check_value(key, args[key])

        if not ok:
            return ""

        n_args[key] = value

    if (not n_args["username"]) or (not n_args["password"]):
        return ""

    database.add_user(
        mode,
        n_args["username"],
        n_args["password"],
        n_args["admin"],
        n_args["name"],
        n_args["rpm"],
        n_args["max_size"],
        n_args["can_list"],
        n_args["mark"],
        n_args["lister"],
    )

    if user and (user.name != n_args["name"]):
        database.change_uploader(user.username, n_args["name"])

    return str(n_args["username"])


def user_edit(user: User, what: str, value: Any) -> tuple[dict[str, Any], int]:
    if not user:
        return {}, 400

    if not what:
        return {}, 400

    ok, value = check_value(what, value)

    if not ok:
        return {}, 400

    database.mod_user([user.username], what, value)
    return {}, 200


def check_auth(username: str, password: str) -> User | None:
    user = get_user(username)

    if not user:
        return None

    if user.username == username:
        if checkpass(user.password, password):
            return user

    return None


def delete_users(usernames: list[str], admin: str) -> tuple[str, int]:
    if not usernames:
        return jsonify(
            {"status": "error", "message": "Usernames were not provided"}
        ), 400

    if admin in usernames:
        return (
            jsonify({"status": "error", "message": "You can't delete yourself"}),
            400,
        )

    for username in usernames:
        do_delete_user(username)

    return jsonify({"status": "ok", "message": "User deleted successfully"}), 200


def delete_user(username: str, admin: str) -> tuple[str, int]:
    if not username:
        return jsonify({"status": "error", "message": "Usename was not provided"}), 400

    if username == admin:
        return jsonify({"status": "error", "message": "You can't delete yourself"}), 400

    do_delete_user(username)
    return jsonify({"status": "ok", "message": "User deleted successfully"}), 200


def do_delete_user(username: str) -> None:
    if not username:
        return

    database.delete_user(username)


def delete_normal_users() -> tuple[str, int]:
    database.delete_normal_users()
    return jsonify({"status": "ok", "message": "Normal users deleted"}), 200


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
    usernames: list[str], what: str, value: str, vtype: str
) -> tuple[dict[str, Any], int]:
    if not what:
        return {}, 400

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

    if new_value is None:
        return {}, 400

    database.mod_user(usernames, what, new_value)
    return {}, 200
