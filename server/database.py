from __future__ import annotations

# Standard
import sys
import sqlite3
from typing import Any
from pathlib import Path
from dataclasses import dataclass, field

# Modules
import utils


schemas = {
    "posts": {
        "id": "integer primary key autoincrement",
        "name": "text key unique default ''",
        "ext": "text default ''",
        "date": "integer default 0",
        "title": "text default ''",
        "views": "integer default 0",
        "original": "text default ''",
        "mtype": "text default ''",
        "view_date": "integer default 0",
        "size": "integer default 0",
        "sample": "text default ''",
        #
        "user": "integer",
        "foreign key(user)": "references users(id)",
    },
    "reactions": {
        "id": "integer primary key autoincrement",
        "value": "text default ''",
        "mode": "text default ''",
        "date": "int default 0",
        #
        "post": "integer",
        "user": "integer",
        "foreign key(post)": "references posts(id)",
        "foreign key(user)": "references users(id)",
    },
    "users": {
        "id": "integer primary key autoincrement",
        "username": "text key unique default ''",
        "password": "text default ''",
        "admin": "integer default 0",
        "name": "text default ''",
        "rpm": "integer default 0",
        "max_size": "integer default 0",
        "reader": "integer default 1",
        "mark": "text default ''",
        "register_date": "integer default 0",
        "last_date": "integer default 0",
        "lister": "integer default 1",
        "poster": "integer default 1",
        "reacter": "integer default 1",
    },
}


def get_schema(what: str) -> str:
    schema = schemas[what]
    return ",".join([f"{k} {v}" for k, v in schema.items()]).strip()


@dataclass
class Post:
    name: str
    ext: str
    date: int
    title: str
    views: int
    original: str
    username: str
    mtype: str
    view_date: int
    size: int
    sample: str
    reactions: list[Reaction] = field(default_factory=list)
    user: User | None = None
    num_reactions: int = 0

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
    reader: bool
    mark: str
    register_date: int
    last_date: int
    lister: bool
    poster: bool
    reacter: bool
    num_posts: int | None = None
    num_reactions: int | None = None


@dataclass
class Reaction:
    id: int
    post: str
    user: str
    value: str
    mode: str
    date: int
    uname: str | None = None


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

    if (
        ("posts" not in tables)
        or ("reactions" not in tables)
        or ("users" not in tables)
    ):
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
    mtype: str,
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
        mtype,
        date,
        size,
        sample,
    ]

    placeholders = ", ".join(["?"] * len(values))
    query = f"insert into posts (name, ext, date, title, views, original, username, mtype, view_date, size, sample) values ({placeholders})"
    c.execute(query, values)
    conn.commit()
    conn.close()


def make_post(row: dict[str, Any]) -> Post:
    return Post(
        id=int(row.get("id")),
        name=row["name"],
        ext=row["ext"],
        date=row["date"],
        title=row.get("title") or "",
        views=int(row.get("views") or 0),
        original=row.get("original") or "",
        username=row.get("username") or "",
        mtype=row.get("mtype") or "",
        view_date=int(row.get("view_date") or 0),
        size=int(row.get("size") or 0),
        sample=row.get("sample") or "",
    )


def get_post(name: str, full_reactions: bool = True) -> Post | None:
    posts = get_posts(name, full_reactions=full_reactions)
    return posts[0] if posts else None


def get_posts(
    post_id: int | None = None, user_id: int | None = None, full_reactions: bool = False
) -> list[Post]:
    check_db()
    conn, c = row_conn()

    if name:
        if user_id:
            c.execute(
                "select * from posts where id = ? and user = ?", (post_id, user_id)
            )
        else:
            c.execute("select * from posts where id = ?", (post_id,))

        rows = [c.fetchone()]
    else:
        if user_id:
            c.execute("select * from posts where user = ?", (user_id,))
        else:
            c.execute("select * from posts")

        rows = c.fetchall()

    posts = []
    rows = [row for row in rows if row]

    for row in rows:
        post = make_post(dict(row))

        if full_reactions:
            reactions = get_reactions(post.id, oconn=conn)

            if reactions:
                post.reactions = reactions
            else:
                post.reactions = []
        else:
            post.reactions = []
            post.num_reactions = get_reaction_count(post.id, oconn=conn)

        user = get_user(post.user, oconn=conn)

        if user:
            post.user = user
        else:
            post.user = None

        posts.append(post)

    conn.close()
    return posts


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


def get_next_post(current: int) -> Post | None:
    check_db()
    conn, c = row_conn()

    c.execute("select * from posts where id = ?", (current,))
    current_row = c.fetchone()

    if not current_row:
        conn.close()
        return None

    date = current_row["date"]

    c.execute(
        "select * from posts p join users u on p.user = u.id where u.listed = 1 and p.date < ? order by p.date desc limit 1",
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
    reader: bool = True,
    mark: str = "",
    lister: bool = True,
    poster: bool = True,
    reacter: bool = True,
    user_id: int | None = None,
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
        reader,
        mark,
        lister,
        poster,
        reacter,
    ]

    columns = [
        "username",
        "password",
        "admin",
        "name",
        "rpm",
        "max_size",
        "reader",
        "mark",
        "lister",
        "poster",
        "reacter",
    ]

    if mode == "add":
        values.extend([date, date])
        columns.extend(["register_date", "last_date"])
        placeholders = ", ".join(["?"] * len(values))
        query = f"insert into users ({', '.join(columns)}) values ({placeholders})"
    elif mode == "edit":
        values.append(user_id)
        clause = ", ".join([f"{col} = ?" for col in columns])
        query = f"update users set {clause} where id = ?"
    else:
        return False

    c.execute(query, values)
    conn.commit()
    conn.close()
    return True


def make_user(row: dict[str, Any]) -> User:
    return User(
        id=int(row.get("id")),
        username=row.get("username") or "",
        password=row.get("password") or "",
        admin=bool(row.get("admin")),
        name=row.get("name") or "",
        rpm=int(row.get("rpm") or 0),
        max_size=int(row.get("max_size") or 0),
        reader=bool(row.get("reader")),
        mark=row.get("mark") or "",
        register_date=int(row.get("register_date") or 0),
        last_date=row.get("last_date") or 0,
        lister=bool(row.get("lister")),
        poster=bool(row.get("poster")),
        reacter=bool(row.get("reacter")),
    )


def get_user(user_id: str, oconn: sqlite3.Connection | None = None) -> User | None:
    users = get_users(user_id, oconn=oconn)
    return users[0] if users else None


def get_users(
    user_id: int | None = None, oconn: sqlite3.Connection | None = None
) -> list[User]:
    if not oconn:
        check_db()
        conn, c = row_conn()
    else:
        conn = oconn
        c = conn.cursor()

    if user_id:
        c.execute("select * from users where id = ?", (user_id,))
        rows = [c.fetchone()]
    else:
        c.execute("select * from users")
        rows = c.fetchall()

    users = []
    rows = [row for row in rows if row]

    for row in rows:
        user = make_user(dict(row))
        user.num_posts = get_post_count(user=row["id"], oconn=conn)
        user.num_reactions = get_reaction_count(user=row["id"], oconn=conn)
        users.append(user)

    if not oconn:
        conn.close()

    return users


def delete_user(user_id: int) -> None:
    check_db()
    conn, c = get_conn()
    c.execute("delete from users where id = ?", (user_id,))
    conn.commit()
    conn.close()


def delete_normal_users() -> None:
    check_db()
    conn, c = get_conn()
    query = "delete from users where admin != 1"
    c.execute(query)
    conn.commit()
    conn.close()


def mod_user(ids: list[str], what: str, value: Any) -> None:
    check_db()
    conn, c = get_conn()
    placeholders = ", ".join("?" for _ in ids)
    query = f"update users set {what} = ? where id in ({placeholders})"
    c.execute(query, (value, *ids))
    conn.commit()
    conn.close()


def update_user_last_date(user_id: int) -> None:
    check_db()
    conn, c = get_conn()

    c.execute("update users set last_date = ? where id = ?", (utils.now(), user_id))

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


def update_file_size(name: str, size: int) -> None:
    check_db()
    conn, c = get_conn()
    c.execute("update posts set size = ? where name = ?", (size, name))
    conn.commit()
    conn.close()


def add_reaction(post: str, user: str, value: str, mode: str) -> int | None:
    check_db()
    conn, c = get_conn()
    cols = ["post", "user", "value", "mode", "date"]
    placeholders = ", ".join("?" for _ in cols)

    c.execute(
        f"insert into reactions ({','.join(cols)}) values ({placeholders}) returning id",
        (post, user, value, mode, utils.now()),
    )

    reaction_id = c.fetchone()[0]
    conn.commit()
    conn.close()
    return int(reaction_id) if reaction_id is not None else None


def make_reaction(row: dict[str, Any]) -> Reaction:
    return Reaction(
        id=int(row.get("id") or 0),
        post=row.get("post") or "",
        user=row.get("user") or "",
        value=row.get("value") or "",
        mode=row.get("mode") or "",
        date=int(row.get("date") or 0),
    )


def get_reaction(
    reaction_id: int, oconn: sqlite3.Connection | None = None
) -> Reaction | None:
    reactions = get_reactions(reaction_id=reaction_id, oconn=oconn)
    return reactions[0] if reactions else None


def get_reactions(
    post_id: int | None = None,
    reaction_id: int | None = None,
    user_id: int | None = None,
    oconn: sqlite3.Connection | None = None,
) -> list[Reaction]:
    if not oconn:
        check_db()
        conn, c = row_conn()
    else:
        conn = oconn
        c = conn.cursor()

    if reaction_id:
        c.execute("select * from reactions where id = ?", (reaction_id,))
        rows = [c.fetchone()]
    elif post_id:
        if user_id:
            c.execute(
                "select * from reactions where post = ? and user = ?",
                (post_id, user_id),
            )
        else:
            c.execute("select * from reactions where post = ?", (post_id,))

        rows = c.fetchall()
    else:
        if user_id:
            c.execute("select * from reactions where user = ?", (user_id,))
        else:
            c.execute("select * from reactions")

        rows = c.fetchall()

    reactions = []
    rows = [row for row in rows if row]

    for row in rows:
        reaction = make_reaction(dict(row))
        c.execute("select * from users where id = ?", (row["user"],))
        user = c.fetchone()

        if user:
            reaction.uname = user["name"]

        reactions.append(reaction)

    if not oconn:
        conn.close()

    return reactions


def get_reaction_count(
    post: int, user: int | None = None, oconn: sqlite3.Connection | None = None
) -> int:
    if not oconn:
        check_db()
        conn, c = get_conn()
    else:
        conn = oconn
        c = conn.cursor()

    if user:
        c.execute(
            "select count(*) from reactions where post = ? and user = ?",
            (post, user),
        )
    else:
        c.execute("select count(*) from reactions where post = ?", (post,))

    result = c.fetchone()
    count = result[0] if result is not None else 0

    if not oconn:
        conn.close()

    return count


def get_post_count(
    user: int | None = None, oconn: sqlite3.Connection | None = None
) -> int:
    if not oconn:
        check_db()
        conn, c = get_conn()
    else:
        conn = oconn
        c = conn.cursor()

    c.execute("select count(*) from posts where user = ?", (user,))
    result = c.fetchone()
    count = result[0] if result is not None else 0

    if not oconn:
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


def delete_reaction(reaction_id: int) -> None:
    check_db()
    conn, c = get_conn()
    c.execute("delete from reactions where id = ?", (reaction_id,))
    conn.commit()
    conn.close()


def delete_all_posts() -> None:
    check_db()
    conn, c = get_conn()
    c.execute("delete from posts")
    conn.commit()
    conn.close()


def delete_all_reactions() -> None:
    check_db()
    conn, c = get_conn()
    c.execute("delete from reactions")
    conn.commit()
    conn.close()


def edit_reaction(reaction_id: int, value: str, mode: str) -> None:
    check_db()
    conn, c = get_conn()

    c.execute(
        "update reactions set value = ?, mode = ? where id = ?", (value, mode, reaction_id)
    )

    conn.commit()
    conn.close()
