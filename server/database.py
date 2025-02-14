from __future__ import annotations

# Standard
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

    def full(self) -> str:
        if self.ext:
            return f"{self.name}.{self.ext}"

        return self.name


@dataclass
class User:
    username: str
    password: str
    name: str
    limit: int
    max: int
    list: bool
    mark: str
    register_date: int
    last_date: int


db_path = "database.sqlite3"


schema_files = {
    "name": "text primary key",
    "ext": "text",
    "date": "int",
    "title": "text",
    "views": "int default 0",
    "original": "text",
    "username": "text",
    "uploader": "text",
    "mtype": "text",
}

schema_users = {
    "username": "text primary key",
    "password": "text",
    "name": "text",
    "limit": "int",
    "max": "int",
    "list": "int",
    "mark": "text",
    "register_date": "int",
    "last_date": "int",
}


def check_db() -> bool:
    path = Path(db_path)

    if not path.exists():
        create_db()
        return False

    check_tables()
    return True


def get_conn() -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    return conn, c


def row_conn() -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    return conn, c


def create_db() -> None:
    conn, c = get_conn()
    c.execute(f"create table files ({schema_files})")
    c.execute(f"create table users ({schema_users})")
    conn.commit()
    conn.close()


def check_tables() -> None:
    conn, c = get_conn()
    c.execute(f"create table if not exists files ({schema_files})")
    c.execute(f"create table if not exists users ({schema_users})")
    conn.commit()
    conn.close()


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
    username: str,
    password: str,
    name: str,
    limit: int,
    max_: int,
    list_: bool,
    mark: str,
) -> None:
    check_db()
    conn, c = get_conn()
    date = utils.now()
    values = [username, password, name, limit, max_, limit, list_, mark]
    placeholders = ", ".join(["?"] * len(values))
    query = f"insert into files (username, password, name, limit, max, limit, list_, mark) values ({placeholders})"
    c.execute(query, values)
    conn.commit()
    conn.close()


def make_user(row: dict[str, Any]) -> User:
    return User(
        username=row.get("username"),
        password=row.get("password"),
        name=row.get("name") or "",
        limit=row.get("limit") or 12,
        max=row.get("max") or 100,
        list=row.get("list") or False,
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


def fill_table() -> None:
    conn, c = get_conn()
    c.execute("pragma table_info(files)")
    columns = [info[1] for info in c.fetchall()]

    for column, c_type in schema_files.items():
        if column not in columns:
            utils.log(f"Adding column: {column}")
            c.execute(f"alter table files add column {column} {c_type}")

    for column, c_type in schema_users.items():
        if column not in columns:
            utils.log(f"Adding column: {column}")
            c.execute(f"alter table users add column {column} {c_type}")

    conn.commit()
    conn.close()

check_db()
fill_table()
