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


def make_user(user: DbUser) -> User:
    reg_date_str = utils.nice_date(user.register_date)
    last_date_str = utils.nice_date(user.last_date)
    admin_str = "A: Yes" if user.admin else "A: No"
    reader_str = "D: Yes" if user.reader else "D: No"
    rpm_fill = user.rpm or config.requests_per_minute
    max_size_fill = user.max_size or config.max_size_user
    lister_str = "L: Yes" if user.lister else "R: No"
    poster_str = "P: Yes" if user.poster else "P: No"
    reacter_str = "R: Yes" if user.reacter else "R: No"
    mage_str = "M: Yes" if user.mage else "M: No"
    num_posts = user.num_posts if user.num_posts else 0
    num_reactions = user.num_reactions if user.num_reactions else 0

    return User(
        user.id,
        user.username,
        user.password,
        user.admin,
        user.name,
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
    )


def get_userlist(user_id: int | None = None) -> list[User]:
    users = database.get_users(user_id=user_id)
    return [make_user(user) for user in users]


def get_users(
    page: int = 1,
    page_size: str = "default",
    query: str = "",
    sort: str = "register_date_desc",
    admin: bool = False,
    user_id: int | None = None,
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

    for user in get_userlist(user_id):
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
            or query in utils.clean_query(user.reader_str)
            or query in utils.clean_query(user.num_posts)
            or query in utils.clean_query(user.num_reactions)
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
    if sort == "register_date_asc":
        users.sort(key=lambda x: x.register_date, reverse=False)
    elif sort == "register_date_desc":
        users.sort(key=lambda x: x.register_date, reverse=True)

    elif sort == "last_date_asc":
        users.sort(key=lambda x: x.last_date, reverse=False)
    elif sort == "last_date_desc":
        users.sort(key=lambda x: x.last_date, reverse=True)

    elif sort == "username_asc":
        users.sort(key=lambda x: x.username, reverse=False)
    elif sort == "username_desc":
        users.sort(key=lambda x: x.username, reverse=True)

    elif sort == "name_asc":
        users.sort(key=lambda x: x.name, reverse=False)
    elif sort == "name_desc":
        users.sort(key=lambda x: x.name, reverse=True)

    elif sort == "rpm_asc":
        users.sort(key=lambda x: x.rpm, reverse=False)
    elif sort == "rpm_desc":
        users.sort(key=lambda x: x.rpm, reverse=True)

    elif sort == "max_size_asc":
        users.sort(key=lambda x: x.max_size, reverse=False)
    elif sort == "max_size_desc":
        users.sort(key=lambda x: x.max_size, reverse=True)

    elif sort == "admin_asc":
        users.sort(key=lambda x: x.admin, reverse=False)
    elif sort == "admin_desc":
        users.sort(key=lambda x: x.admin, reverse=True)

    elif sort == "reader_asc":
        users.sort(key=lambda x: x.reader, reverse=False)
    elif sort == "reader_desc":
        users.sort(key=lambda x: x.reader, reverse=True)

    elif sort == "lister_asc":
        users.sort(key=lambda x: x.lister, reverse=False)
    elif sort == "lister_desc":
        users.sort(key=lambda x: x.lister, reverse=True)

    elif sort == "poster_asc":
        users.sort(key=lambda x: x.poster, reverse=False)
    elif sort == "poster_desc":
        users.sort(key=lambda x: x.poster, reverse=True)

    elif sort == "reacter_asc":
        users.sort(key=lambda x: x.reacter, reverse=False)
    elif sort == "reacter_desc":
        users.sort(key=lambda x: x.reacter, reverse=True)

    elif sort == "num_posts_asc":
        users.sort(key=lambda x: x.num_posts, reverse=False)
    elif sort == "num_posts_desc":
        users.sort(key=lambda x: x.num_posts, reverse=True)

    elif sort == "num_reactions_asc":
        users.sort(key=lambda x: x.num_reactions, reverse=False)
    elif sort == "num_reactions_desc":
        users.sort(key=lambda x: x.num_reactions, reverse=True)

    elif sort == "mark_asc":
        users.sort(key=lambda x: x.mark, reverse=False)
    elif sort == "mark_desc":
        users.sort(key=lambda x: x.mark, reverse=True)

    elif sort == "mage_asc":
        users.sort(key=lambda x: x.mage, reverse=False)
    elif sort == "mage_desc":
        users.sort(key=lambda x: x.mage, reverse=True)


def get_user(user_id: int | None = None, username: str | None = None) -> User | None:
    if (not user_id) and (not username):
        return None

    users = database.get_users(user_id=user_id, username=username)
    user = users[0] if users else None

    if not user:
        return None

    return make_user(user)


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
        ids.remove(user.id)

    ok, checked_value = check_value(None, what, new_value)

    if not ok:
        return utils.bad("Invalid value")

    if what == "username":
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

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    password_2 = request.form.get("password_2", "")
    code = request.form.get("code", "")
    name = request.form.get("name", "").strip()

    if config.register_code:
        if code != config.register_code:
            return False, "Invalid code", None

    if (not username) or (not password) or (not password_2) or (not name):
        return False, "Missing details", None

    if password != password_2:
        return False, "Passwords do not match", None

    ok, username = check_value(None, "username", username)

    if not ok:
        return False, "Invalid username", None

    ok, password = check_value(None, "password", password)

    if not ok:
        return False, "Invalid password", None

    ok, name = check_value(None, "name", name)

    if not ok:
        return False, "Invalid name", None

    if database.username_exists(username):
        return False, "User already exists", None

    user_id = database.add_user(
        "add", username=username, password=password, name=name, mage=config.default_mage
    )

    user = get_user(user_id)

    if not user:
        return False, "User not found", None

    return True, "User registered successfully", user
