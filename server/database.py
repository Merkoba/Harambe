from __future__ import annotations

# Standard
import sqlite3
from typing import Any
from pathlib import Path
from dataclasses import dataclass

# Libraries
from werkzeug.security import generate_password_hash

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

    def full(self) -> str:
        if self.ext:
            return f"{self.name}.{self.ext}"

        return self.name


@dataclass
class User:
    username: str
    password: str
    name: str
    rpm: int
    max_size: int
    can_list: bool
    mark: str
    register_date: int
    last_date: int


db_path = "database.sqlite3"


def check_db() -> bool:
    path = Path(db_path)
    return path.exists()


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
    if not check_db():
        return

    conn, c = get_conn()
    date = utils.now()
    values = [name, ext, date, title, 0, original, username, uploader, mtype]
    placeholders = ", ".join(["?"] * len(values))
    query = f"insert into files (name, ext, date, title, views, original, username, uploader, mtype) values ({placeholders})"
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
    )


def get_file(name: str) -> File | None:
    if not check_db():
        return None

    conn, c = row_conn()
    c.execute("select * from files where name = ?", (name,))
    row = c.fetchone()
    conn.close()

    if row:
        return make_file(dict(row))

    return None


def get_files() -> dict[str, File]:
    if not check_db():
        return {}

    conn, c = row_conn()
    c.execute("select * from files")
    rows = c.fetchall()
    conn.close()

    return {row["name"]: make_file(dict(row)) for row in rows}


def remove_file(name: str) -> None:
    if not check_db():
        return

    conn, c = get_conn()
    c.execute("delete from files where name = ?", (name,))
    conn.commit()
    conn.close()


def increase_views(name: str) -> None:
    if not check_db():
        return

    conn, c = get_conn()
    c.execute("update files set views = views + 1 where name = ?", (name,))
    conn.commit()
    conn.close()


def edit_title(name: str, title: str) -> None:
    if not check_db():
        return

    conn, c = get_conn()
    c.execute("update files set title = ? where name = ?", (title, name))
    conn.commit()
    conn.close()


def add_user(
    mode: str,
    username: str,
    password: str,
    name: str,
    rpm: int,
    max_: int,
    list_: bool,
    mark: str,
) -> None:
    if not check_db():
        return

    if (not username) or (not password):
        return

    conn, c = get_conn()
    hashed_password = generate_password_hash(password)
    date = utils.now()

    values = [
        username,
        hashed_password,
        name or "",
        rpm or 12,
        max_size or 0,
        can_list or 0,
        mark or "",
    ]

    if mode == "add":
        values.extend([date, date])
        placeholders = ", ".join(["?"] * len(values))
        query = f"insert into files (username, password, name, rpm, max_size, can_list, mark, register_date, last_date) values ({placeholders})"
    elif mode == "edit":
        values.append(username)
        query = f"update users set username = ?, password = ?, name = ?, rpm = ?, max_size = ?, can_list = ?, mark = ? where username = ?"

    c.execute(query, values)
    conn.commit()
    conn.close()


def make_user(row: dict[str, Any]) -> User:
    return User(
        username=row.get("username"),
        password=row.get("password"),
        name=row.get("name") or "",
        rpm=row.get("rpm") or 12,
        max_size=row.get("max_size") or 100,
        can_list=row.get("can_list") or 0,
        mark=row.get("mark") or "",
        register_date=row.get("register_date") or 0,
        last_date=row.get("last_date") or 0,
    )


def get_users() -> dict[str, File]:
    if not check_db():
        return {}

    conn, c = row_conn()
    c.execute("select * from users")
    rows = c.fetchall()
    conn.close()

    return {row["name"]: make_user(dict(row)) for row in rows}
