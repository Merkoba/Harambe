from __future__ import annotations

# Standard
import sys
import sqlite3
from typing import Any
from pathlib import Path
from dataclasses import dataclass

# Modules
import utils


@dataclass
class Post:
    name: str
    ext: str
    date: int
    title: str
    views: int
    original: str
    username: str
    uploader: str
    mtype: str
    view_date: int
    listed: bool
    size: int
    sample: str

    def full(self) -> str:
        if self.ext:
            return f"{self.name}.{self.ext}"

        return self.name

    def original_full(self) -> str:
        if self.ext:
            return f"{self.original}.{self.ext}"

        return self.original


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
    lister: bool
    posts: int
    reacter: bool


@dataclass
class Reaction:
    post: str
    user: str
    uname: str
    value: str
    mode: str
    date: int


db_path = "database.sqlite3"


def check_db() -> None:
    msg = "Database not found or incomplete. Run schema.py"
    path = Path(db_path)

    if not path.exists():
        sys.exit(msg)

    conn, c = get_conn()
    c.execute("select name from sqlite_master where type='table'")
    tables = [table[0] for table in c.fetchall()]
    conn.close()

    if ("posts" not in tables) or ("users" not in tables):
        sys.exit(msg)


def get_conn() -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    return conn, c


def row_conn() -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    return conn, c


def add_post(
    name: str,
    ext: str,
    title: str,
    original: str,
    username: str,
    uploader: str,
    mtype: str,
    listed: bool,
    size: int,
    sample: str,
) -> None:
    check_db()
    conn, c = get_conn()
    date = utils.now()

    values = [
        name,
        ext,
        date,
        title,
        0,
        original,
        username,
        uploader,
        mtype,
        date,
        listed,
        size,
        sample,
    ]

    placeholders = ", ".join(["?"] * len(values))
    query = f"insert into posts (name, ext, date, title, views, original, username, uploader, mtype, view_date, listed, size, sample) values ({placeholders})"
    c.execute(query, values)
    conn.commit()
    conn.close()


def make_post(row: dict[str, Any]) -> Post:
    return Post(
        name=row["name"],
        ext=row["ext"],
        date=row["date"],
        title=row.get("title") or "",
        views=row.get("views") or 0,
        original=row.get("original") or "",
        username=row.get("username") or "",
        uploader=row.get("uploader") or "",
        mtype=row.get("mtype") or "",
        view_date=row.get("view_date") or 0,
        listed=bool(row.get("listed")),
        size=row.get("size") or 0,
        sample=row.get("sample") or "",
    )


def get_post(name: str) -> Post | None:
    check_db()
    conn, c = row_conn()
    c.execute("select * from posts where name = ?", (name,))
    row = c.fetchone()
    conn.close()

    if row:
        return make_post(dict(row))

    return None


def get_posts() -> list[Post]:
    check_db()
    conn, c = row_conn()
    c.execute("select * from posts")
    rows = c.fetchall()
    conn.close()

    return [make_post(dict(row)) for row in rows]


def delete_post(name: str) -> None:
    check_db()
    conn, c = get_conn()
    c.execute("delete from posts where name = ?", (name,))
    conn.commit()
    conn.close()


def increase_post_views(name: str) -> None:
    check_db()
    conn, c = get_conn()
    c.execute(
        "update posts set views = views + 1, view_date = ? where name = ?",
        (utils.now(), name),
    )
    conn.commit()
    conn.close()


def edit_post_title(name: str, title: str) -> None:
    check_db()
    conn, c = get_conn()
    c.execute("update posts set title = ? where name = ?", (title, name))
    conn.commit()
    conn.close()


def get_next_post(current: str) -> Post | None:
    check_db()
    conn, c = row_conn()

    c.execute("select * from posts where name = ?", (current,))
    current_row = c.fetchone()

    if not current_row:
        conn.close()
        return None

    date = current_row["date"]
    c.execute(
        "select * from posts where date < ? and listed = 1 order by date desc limit 1",
        (date,),
    )
    next_row = c.fetchone()
    conn.close()

    if next_row:
        return make_post(dict(next_row))

    return None


def add_user(
    mode: str,
    username: str,
    password: str,
    admin: bool = False,
    name: str = "",
    rpm: int = 0,
    max_size: int = 0,
    can_list: bool = True,
    mark: str = "",
    lister: bool = True,
    reacter: bool = True,
) -> bool:
    check_db()

    if (not username) or (not password):
        return False

    conn, c = get_conn()
    date = utils.now()

    values = [
        username,
        password,
        admin,
        name,
        rpm,
        max_size,
        can_list,
        mark,
        lister,
        reacter,
    ]

    columns = [
        "username",
        "password",
        "admin",
        "name",
        "rpm",
        "max_size",
        "can_list",
        "mark",
        "lister",
        "reacter",
    ]

    if mode == "add":
        c.execute("select * from users where username = ?", (username,))

        if c.fetchone():
            conn.close()
            return False

        values.extend([date, date, 0])
        columns.extend(["register_date", "last_date", "posts"])
        placeholders = ", ".join(["?"] * len(values))
        query = f"insert into users ({', '.join(columns)}) values ({placeholders})"
    elif mode == "edit":
        values.append(username)
        clause = ", ".join([f"{col} = ?" for col in columns])
        query = f"update users set {clause} where username = ?"
    else:
        return False

    c.execute(query, values)
    conn.commit()
    conn.close()
    return True


def make_user(row: dict[str, Any]) -> User:
    return User(
        username=row.get("username") or "",
        password=row.get("password") or "",
        admin=bool(row.get("admin")),
        name=row.get("name") or "",
        rpm=row.get("rpm") or 0,
        max_size=row.get("max_size") or 0,
        can_list=bool(row.get("can_list")),
        mark=row.get("mark") or "",
        register_date=row.get("register_date") or 0,
        last_date=row.get("last_date") or 0,
        lister=bool(row.get("lister")),
        posts=row.get("posts") or 0,
        reacter=bool(row.get("reacter")),
    )


def get_users() -> list[User]:
    check_db()
    conn, c = row_conn()
    c.execute("select * from users")
    rows = c.fetchall()
    conn.close()

    return [make_user(dict(row)) for row in rows]


def get_user(username: str) -> User | None:
    check_db()
    conn, c = row_conn()
    c.execute("select * from users where username = ?", (username,))
    row = c.fetchone()
    conn.close()

    if row:
        return make_user(dict(row))

    return None


def delete_user(username: str) -> None:
    check_db()
    conn, c = get_conn()
    c.execute("delete from users where username = ?", (username,))
    conn.commit()
    conn.close()


def delete_normal_users() -> None:
    check_db()
    conn, c = get_conn()
    query = "delete from users where admin != 1"
    c.execute(query)
    conn.commit()
    conn.close()


def mod_user(usernames: list[str], what: str, value: Any) -> None:
    check_db()
    conn, c = get_conn()
    placeholders = ", ".join("?" for _ in usernames)
    query = f"update users set {what} = ? where username in ({placeholders})"
    c.execute(query, (value, *usernames))
    conn.commit()
    conn.close()


def update_user_last_date(username: str) -> None:
    check_db()
    conn, c = get_conn()

    c.execute(
        "update users set last_date = ? where username = ?", (utils.now(), username)
    )

    conn.commit()
    conn.close()


def get_random_post(ignore_names: list[str]) -> Post | None:
    check_db()
    conn, c = row_conn()
    query = "select * from posts where name not in ({}) and mtype is not null and mtype != '' and listed = 1 order by random() limit 1"
    placeholders = ", ".join("?" for _ in ignore_names)
    c.execute(query.format(placeholders), ignore_names)
    row = c.fetchone()
    conn.close()

    if row:
        return make_post(dict(row))

    return None


def increase_user_posts(username: str) -> None:
    check_db()
    conn, c = get_conn()
    c.execute("update users set posts = posts + 1 where username = ?", (username,))
    conn.commit()
    conn.close()


def update_file_size(name: str, size: int) -> None:
    check_db()
    conn, c = get_conn()
    c.execute("update posts set size = ? where name = ?", (size, name))
    conn.commit()
    conn.close()


def change_uploader(username: str, new_name: str) -> None:
    check_db()
    conn, c = get_conn()
    c.execute("update posts set uploader = ? where username = ?", (new_name, username))
    conn.commit()
    conn.close()


def add_reaction(post: str, user: str, uname: str, value: str, mode: str) -> None:
    check_db()
    conn, c = get_conn()
    cols = ["post", "user", "uname", "value", "mode", "date"]
    placeholders = ", ".join("?" for _ in cols)

    c.execute(
        f"insert into reactions ({','.join(cols)}) values ({placeholders})",
        (post, user, uname, value, mode, utils.now()),
    )

    conn.commit()
    conn.close()


def make_reaction(row: dict[str, Any]) -> Reaction:
    return Reaction(
        post=row.get("post") or "",
        user=row.get("user") or "",
        uname=row.get("uname") or "",
        value=row.get("value") or "",
        mode=row.get("mode") or "",
        date=row.get("date") or 0,
    )


def get_reactions(post: str) -> list[Reaction]:
    check_db()
    conn, c = row_conn()
    c.execute("select * from reactions where post = ?", (post,))
    rows = c.fetchall()
    conn.close()

    return [make_reaction(dict(row)) for row in rows]


def get_reaction_count(post: str, user: str) -> int:
    check_db()
    conn, c = get_conn()

    c.execute(
        "select count(*) from reactions where post = ? and user = ?",
        (post, user),
    )

    result = c.fetchone()
    count = result[0] if result is not None else 0
    conn.close()
    return count


def get_latest_post() -> Post | None:
    check_db()
    conn, c = row_conn()
    c.execute("select * from posts order by date desc limit 1")
    row = c.fetchone()
    conn.close()

    if row:
        return make_post(dict(row))

    return None
