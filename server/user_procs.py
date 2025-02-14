from __future__ import annotations

# Standard
from dataclasses import dataclass

# Libraries
from flask import Request  # type: ignore
from werkzeug.security import generate_password_hash as hashpass  # type: ignore

# Modules
from config import config
import database


@dataclass
class User:
    username: str
    password: str
    admin: bool
    name: str
    rpm: int
    max_size: int
    can_list: bool
    mark: str
    register_date: int
    last_date: int


userlist: list[User] = []


def update_userlist() -> None:
    userlist.clear()

    for db_user in database.get_users():
        user = User(
            db_user.username,
            db_user.password,
            db_user.admin,
            db_user.name,
            db_user.rpm,
            db_user.max_size,
            db_user.can_list,
            db_user.mark,
            db_user.register_date,
            db_user.last_date,
        )

        userlist.append(user)


def get_users(
    page: int = 1,
    page_size: str = "default",
    query: str = "",
    sort: str = "date",
) -> tuple[list[User], str, bool]:
    psize = 0

    if page_size == "default":
        psize = config.admin_page_size
    elif page_size == "all":
        pass  # Don't slice later
    else:
        psize = int(page_size)

    users = []
    query = query.lower()

    for user in userlist:
        ok = not query or query in user.username

        if not ok:
            continue

        users.append(user)

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

    total_str = f"{len(users)}"

    if psize > 0:
        start_index = (page - 1) * psize
        end_index = start_index + psize
        has_next_page = end_index < len(users)
        users = users[start_index:end_index]
    else:
        has_next_page = False

    return users, total_str, has_next_page


def get_user(username: str) -> User | None:
    for user in userlist:
        if user.username == username:
            return user

    return None


def edit_user(request: Request) -> bool:
    args = {}
    args["username"] = request.form.get("username")
    args["password"] = request.form.get("password")
    args["admin"] = request.form.get("admin") or False
    args["name"] = request.form.get("name", "")
    args["rpm"] = int(request.form.get("rpm") or 0)
    args["max_size"] = int(request.form.get("max_size") or 0)
    args["can_list"] = request.form.get("can_list", "")
    args["mark"] = request.form.get("mark", "")

    user = get_user(args["username"])
    mode = "add" if user is None else "edit"
    n_args = {}

    def get_value(what: str) -> None:
        value = None

        if args[what]:
            value = args[what]

            if what == "password":
                value = hashpass(value)

        if not value:
            if user and getattr(user, what):
                value = getattr(user, what)

        n_args[what] = value

    for key in args:
        get_value(key)

    if (not n_args["username"]) or (not n_args["password"]):
        return False

    if database.add_user(
        mode,
        n_args["username"],
        n_args["password"],
        n_args["admin"],
        n_args["name"],
        n_args["rpm"],
        n_args["max_size"],
        n_args["can_list"],
        n_args["mark"],
    ):
        update_userlist()
        return True

    return False


def check_auth(username: str, password: str) -> User | None:
    for user in userlist:
        if user.username == username:
            if user.password == password:
                return user

    return None
