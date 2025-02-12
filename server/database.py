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
    uploader: str
    key: str


db_path = "database.sqlite3"


schema = {
    "name": "text primary key",
    "ext": "text",
    "date": "int",
    "title": "text",
    "views": "int default 0",
    "original": "text",
    "uploader": "text",
    "key": "text",
}


def check_db() -> bool:
    path = Path(db_path)

    if not path.exists():
        create_db()
        return False

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

    c.execute(
        f"""create table files (
            {schema}
        )"""
    )

    conn.commit()
    conn.close()


def add_file(
    name: str, ext: str, title: str, original: str, uploader: str, key: str
) -> None:
    check_db()
    conn, c = get_conn()
    date = utils.now()

    c.execute(
        "insert into files (name, ext, date, title, views, original, uploader, key) values (?, ?, ?, ?, ?, ?, ?, ?)",
        (name, ext, date, title, 0, original, uploader, key),
    )

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
        uploader=row.get("uploader") or "",
        key=row.get("key") or "",
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


def fill_table() -> None:
    conn, c = get_conn()
    c.execute("pragma table_info(files)")
    columns = [info[1] for info in c.fetchall()]

    for column, c_type in schema.items():
        if column not in columns:
            utils.log(f"Adding column: {column}")
            c.execute(f"alter table files add column {column} {c_type}")

    conn.commit()
    conn.close()


fill_table()
