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
class File:
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

    def full(self) -> str:
        if self.ext:
            return f"{self.name}.{self.ext}"

        return self.name


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

    if ("files" not in tables) or ("users" not in tables):
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


def add_file(
    name: str,
    ext: str,
    title: str,
    original: str,
    username: str,
    uploader: str,
    mtype: str,
) -> None:
    check_db()
    conn, c = get_conn()
    date = utils.now()
    values = [name, ext, date, title, 0, original, username, uploader, mtype, date]
    placeholders = ", ".join(["?"] * len(values))
    query = f"insert into files (name, ext, date, title, views, original, username, uploader, mtype, view_date) values ({placeholders})"
    c.execute(query, values)
    conn.commit()
    conn.close()


def make_file(row: dict[str, Any]) -> File:
    return File(
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
    )


def get_file(name: str) -> File | None:
    check_db()
    conn, c = row_conn()
    c.execute("select * from files where name = ?", (name,))
    row = c.fetchone()
    conn.close()

    if row:
        return make_file(dict(row))

    return None


def get_files() -> dict[str, File]:
    check_db()
    conn, c = row_conn()
    c.execute("select * from files")
    rows = c.fetchall()
    conn.close()

    return {row["name"]: make_file(dict(row)) for row in rows}


def delete_file(name: str) -> None:
    check_db()
    conn, c = get_conn()
    c.execute("delete from files where name = ?", (name,))
    conn.commit()
    conn.close()


def increase_views(name: str) -> None:
    check_db()
    conn, c = get_conn()
    c.execute(
        "update files set views = views + 1, view_date = ? where name = ?",
        (utils.now(), name),
    )
    conn.commit()
    conn.close()


def edit_title(name: str, title: str) -> None:
    check_db()
    conn, c = get_conn()
    c.execute("update files set title = ? where name = ?", (title, name))
    conn.commit()
    conn.close()


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
        mark or "",
    ]

    if mode == "add":
        values.extend([date, date])
        placeholders = ", ".join(["?"] * len(values))
        query = f"insert into users (username, password, admin, name, rpm, max_size, can_list, mark, register_date, last_date) values ({placeholders})"
    elif mode == "edit":
        values.append(username)
        query = "update users set username = ?, password = ?, admin = ?, name = ?, rpm = ?, max_size = ?, can_list = ?, mark = ? where username = ?"
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
        admin=row.get("admin") or False,
        name=row.get("name") or "",
        rpm=row.get("rpm") or 0,
        max_size=row.get("max_size") or 0,
        can_list=bool(row.get("can_list")) or False,
        mark=row.get("mark") or "",
        register_date=row.get("register_date") or 0,
        last_date=row.get("last_date") or 0,
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
