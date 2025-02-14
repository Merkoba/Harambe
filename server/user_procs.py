# Standard
from dataclasses import dataclass

# Libraries
from flask import Request

# Modules
import database


@dataclass
class User:
    username: str
    name: str
    rpm: int
    max_size: int
    can_list: bool
    mark: str
    register_date: int
    last_date: int


userlist: list[User] = []


def update_userlist():
    for db_user in database.get_users():
        user = User(
            db_user.username,
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
    now = utils.now()
    query = query.lower()

    for user in userlist:
        ok = (
            not query
            or query in u.username()
        )

        if not ok:
            continue

        users.append(f)

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

    total_str = f"{len(users)} Users"

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

def edit_user(request: Request) -> None:
    username = request.form.get("username")
    password = request.form.get("password")
    name = request.form.get("name")
    rpm = int(request.form.get("rpm"))
    max_size = int(request.form.get("max_size"))
    can_list = request.form.get("can_list")
    mark = request.form.get("mark")

    user = get_user(username)
    mode = "add" if user is None else "edit"
    passw = user.password if user is not None else password

    database.add_user(
        mode,
        username,
        password,
        name,
        rpm,
        max_size,
        can_list,
        mark,
    )

    update_userlist()