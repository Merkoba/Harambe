from __future__ import annotations

# Standard
from dataclasses import dataclass

# Libraries
from flask import Request, jsonify  # type: ignore
from werkzeug.security import generate_password_hash as hashpass  # type: ignore
from werkzeug.security import check_password_hash as checkpass  # pyright: ignore

# Modules
import utils
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
    register_date_str: str
    last_date: int
    last_date_str: str


userlist: list[User] = []


def update_userlist() -> None:
    userlist.clear()

    for user in database.get_users():
        reg_date_str = utils.nice_date(user.register_date)
        last_date_str = utils.nice_date(user.last_date)

        u = User(
            user.username,
            user.password,
            user.admin,
            user.name,
            user.rpm,
            user.max_size,
            user.can_list,
            user.mark,
            user.register_date,
            reg_date_str,
            user.last_date,
            last_date_str,
        )

        userlist.append(u)


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


def edit_user(request: Request, username: str) -> bool:
    if (not request) or (not username):
        return False

    args = {}

    args["username"] = [request.form.get("username"), "string"]
    args["password"] = [request.form.get("password"), "string"]
    args["name"] = [request.form.get("name"), "string"]
    args["rpm"] = [request.form.get("rpm"), "int"]
    args["max_size"] = [request.form.get("max_size"), "int"]
    args["mark"] = [request.form.get("mark"), "string"]
    args["admin"] = [request.form.get("admin") or False, "bool"]
    args["can_list"] = [request.form.get("can_list") or False, "bool"]

    uname = args["username"][0]

    if not uname:
        return False

    if uname == username:
        args["admin"][0] = True

    user = get_user(uname)
    mode = "add" if user is None else "edit"
    n_args = {}

    def get_value(what: str) -> None:
        value, vtype = args[what]

        if what == "password":
            if value:
                value = hashpass(value)
            elif user and user.password:
                value = user.password

        if value:
            if vtype == "int":
                value = int(value)
            elif vtype == "string":
                value = str(value)
            elif vtype == "bool":
                value = bool(value)

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
            if checkpass(user.password, password):
                return user

            break

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

    return jsonify({"status": "ok", "message": "File deleted successfully"}), 200


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
    update_userlist()


def delete_normal_users() -> tuple[str, int]:
    database.delete_normal_users()
    update_userlist()
    return jsonify({"status": "ok", "message": "Normal users deleted"}), 200
