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
    comment: str
    views: int = 0


db_path = "database.sqlite3"


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
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute(
        """create table files (
        name text primary key,
        ext text,
        date int,
        comment text,
        views int default 0
    )"""
    )

    conn.commit()
    conn.close()


def add_file(name: str, ext: str, comment: str) -> None:
    check_db()
    conn, c = get_conn()
    date = utils.now()

    c.execute(
        "insert into files (name, ext, date, comment, views) values (?, ?, ?, ?, ?)",
        (name, ext, date, comment, 0),
    )

    conn.commit()
    conn.close()


def make_file(row: dict[str, Any]) -> File:
    return File(
        name=row["name"],
        ext=row["ext"],
        date=row["date"],
        comment=row.get("comment", ""),
        views=row.get("views", 0),
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
