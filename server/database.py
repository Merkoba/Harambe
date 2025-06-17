from __future__ import annotations

# Standard
import sys
import sqlite3
from typing import Any
from pathlib import Path
from dataclasses import dataclass, field

# Modules
import utils
from config import config


schemas = {
    "posts": {
        "id": "integer primary key autoincrement",
        "name": "text unique default ''",
        "ext": "text default ''",
        "date": "integer default 0",
        "title": "text default ''",
        "description": "text default ''",
        "views": "integer default 0",
        "original": "text default ''",
        "mtype": "text default ''",
        "view_date": "integer default 0",
        "size": "integer default 0",
        "value": "text default ''",
        "file_hash": "text default 'none'",
        "privacy": "text default 'public'",
        # Foreign keys
        "user": "integer",
        # On Delete
        "foreign key(user)": "references users(id) on delete cascade",
    },
    "reactions": {
        "id": "integer primary key autoincrement",
        "value": "text default ''",
        "date": "int default 0",
        # Foreign keys
        "post": "integer",
        "user": "integer",
        # On Delete
        "foreign key(post)": "references posts(id) on delete cascade",
        "foreign key(user)": "references users(id) on delete cascade",
    },
    "users": {
        "id": "integer primary key autoincrement",
        "username": "text unique default ''",
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
        "mage": "integer default 0",
    },
}


indexes = {
    "posts": [
        "CREATE INDEX IF NOT EXISTS idx_posts_id ON posts(id);",
        "CREATE INDEX IF NOT EXISTS idx_posts_name ON posts(name);",
        "CREATE INDEX IF NOT EXISTS idx_posts_user ON posts(user);",
        "CREATE INDEX IF NOT EXISTS idx_posts_date ON posts(date);",
        "CREATE INDEX IF NOT EXISTS idx_posts_file_hash ON posts(file_hash);",
    ],
    "reactions": [
        "CREATE INDEX IF NOT EXISTS idx_reactions_id ON reactions(id);",
        "CREATE INDEX IF NOT EXISTS idx_reactions_post ON reactions(post);",
        "CREATE INDEX IF NOT EXISTS idx_reactions_user ON reactions(user);",
        "CREATE INDEX IF NOT EXISTS idx_reactions_date ON reactions(date);",
    ],
    "users": [
        "CREATE INDEX IF NOT EXISTS idx_users_id ON users(id);",
        "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);",
    ],
}


def get_schema(what: str) -> str:
    schema = schemas[what]
    return ",".join([f"{k} {v}" for k, v in schema.items()]).strip()


@dataclass
class Post:
    id: int
    user: int
    name: str
    ext: str
    date: int
    title: str
    views: int
    original: str
    mtype: str
    view_date: int
    size: int
    file_hash: str
    privacy: str
    description: str
    value: str
    reactions: list[Reaction] = field(default_factory=list)
    num_reactions: int = 0
    author: User | None = None


@dataclass
class Reaction:
    id: int
    post: int
    user: int
    value: str
    date: int
    parent: Post | None = None
    author: User | None = None


@dataclass
class User:
    id: int
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
    mage: bool
    num_posts: int | None = None
    num_reactions: int | None = None


@dataclass
class Connection:
    conn: sqlite3.Connection
    c: sqlite3.Cursor

    def tuple(self) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        return (self.conn, self.c)


db_path = "database.sqlite3"


def check_db() -> None:
    msg = "Database not found or incomplete. Run schema.py"
    path = Path(db_path)

    if not path.exists():
        sys.exit(msg)

    connection = get_conn()
    conn, c = connection.tuple()
    c.execute("select name from sqlite_master where type='table'")
    tables = [table[0] for table in c.fetchall()]
    conn.close()

    if (
        ("posts" not in tables)
        or ("reactions" not in tables)
        or ("users" not in tables)
    ):
        sys.exit(msg)


def get_conn(connection: Connection | None = None) -> Connection:
    if not connection:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys = ON;")
        return Connection(conn, c)

    return connection


def row_conn() -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    return conn, c


def add_post(
    user_id: int,
    name: str,
    ext: str,
    title: str,
    original: str,
    mtype: str,
    size: int,
    file_hash: str,
    privacy: str,
    description: str,
    value: str,
) -> None:
    connection = get_conn()
    conn, c = connection.tuple()
    date = utils.now()

    values = [
        user_id,
        name,
        ext,
        date,
        title,
        0,
        original,
        mtype,
        date,
        size,
        file_hash,
        privacy,
        description,
        value,
    ]

    placeholders = ", ".join(["?"] * len(values))
    query = f"insert into posts (user, name, ext, date, title, views, original, mtype, view_date, size, file_hash, privacy, description, value) values ({placeholders})"
    c.execute(query, values)
    conn.commit()
    conn.close()


def make_post(row: dict[str, Any]) -> Post:
    return Post(
        id=int(row.get("id") or 0),
        user=int(row.get("user") or 0),
        name=row["name"],
        ext=row["ext"],
        date=row["date"],
        title=row.get("title") or "",
        views=int(row.get("views") or 0),
        original=row.get("original") or "",
        mtype=row.get("mtype") or "",
        view_date=int(row.get("view_date") or 0),
        size=int(row.get("size") or 0),
        file_hash=row.get("file_hash") or "none",
        privacy=row.get("privacy") or "none",
        description=row.get("description") or "",
        value=row.get("value") or "",
    )


def get_posts(
    post_id: int | None = None,
    name: str | None = None,
    user_id: int | None = None,
    file_hash: str | None = None,
    title: str | None = None,
    description: str | None = None,
    value: str | None = None,
    extra: bool = True,
    full_reactions: bool = False,
    increase: bool = False,
    names: list[str] | None = None,
    ignore_ids: list[int] | None = None,
    only_public: bool = False,
    oconn: Connection | None = None,
) -> list[Post]:
    connection = get_conn(oconn)
    conn, c = connection.tuple()
    pub = " and privacy = 'public'" if only_public else ""

    if post_id:
        c.execute(f"select * from posts where id = ?{pub}", (post_id,))
        rows = [c.fetchone()]
    elif names:
        placeholders = ", ".join("?" for _ in names)
        c.execute(f"select * from posts where name in ({placeholders}){pub}", names)
        rows = c.fetchall()
    elif name:
        c.execute(f"select * from posts where name = ?{pub}", (name,))
        rows = [c.fetchone()]
    elif user_id:
        c.execute(f"select * from posts where user = ?{pub}", (user_id,))
        rows = c.fetchall()
    elif file_hash:
        c.execute(f"select * from posts where file_hash = ?{pub}", (file_hash,))
        rows = c.fetchall()
    elif title and description:
        c.execute(
            f"select * from posts where title = ? and description = ?{pub}",
            (title, description),
        )

        rows = c.fetchall()
    elif title:
        c.execute(f"select * from posts where title = ?{pub}", (title,))
        rows = c.fetchall()
    elif value:
        c.execute(f"select * from posts where value = ?{pub}", (value,))
        rows = c.fetchall()
    elif only_public:
        c.execute("select * from posts where privacy = 'public'")
        rows = c.fetchall()
    else:
        c.execute("select * from posts")
        rows = c.fetchall()

    posts = []
    rows = [row for row in rows if row]

    if ignore_ids:
        rows = [row for row in rows if row["id"] not in ignore_ids]

    now = utils.now()

    for row in rows:
        post = make_post(dict(row))

        if extra:
            users = get_users(post.user, oconn=connection)
            user = users[0] if users else None

            if user:
                post.author = user
            else:
                post.author = None

            if full_reactions:
                reactions = get_reactions(post_id=post.id, post=post, oconn=connection)

                if reactions:
                    post.reactions = reactions
                else:
                    post.reactions = []
            else:
                post.reactions = []
                post.num_reactions = get_reaction_count(post.id, oconn=connection)
                last_reaction = get_last_reaction(post.id, oconn=connection)

                if last_reaction:
                    post.reactions = [last_reaction]
                else:
                    post.reactions = []

        if increase:
            diff = now - post.view_date

            if diff > config.view_delay:
                increase_post_views(post.id, oconn=connection)

        posts.append(post)

    if not oconn:
        conn.close()

    return posts


def delete_post(post_id: int) -> None:
    connection = get_conn()
    conn, c = connection.tuple()
    c.execute("delete from posts where id = ?", (post_id,))
    conn.commit()
    conn.close()


def increase_post_views(post_id: int, oconn: Connection | None = None) -> None:
    connection = get_conn(oconn)
    conn, c = connection.tuple()

    c.execute(
        "update posts set views = views + 1, view_date = ? where id = ?",
        (utils.now(), post_id),
    )

    conn.commit()

    if not oconn:
        conn.close()


def edit_post_title(post_id: int, title: str) -> None:
    connection = get_conn()
    conn, c = connection.tuple()
    c.execute("update posts set title = ? where id = ?", (title, post_id))
    conn.commit()
    conn.close()


def edit_post_description(post_id: int, description: str) -> None:
    connection = get_conn()
    conn, c = connection.tuple()
    c.execute("update posts set description = ? where id = ?", (description, post_id))
    conn.commit()
    conn.close()


def edit_post_original(post_id: int, original: str) -> None:
    connection = get_conn()
    conn, c = connection.tuple()
    c.execute("update posts set original = ? where id = ?", (original, post_id))
    conn.commit()
    conn.close()


def edit_post_ext(post_id: int, ext: str) -> None:
    connection = get_conn()
    conn, c = connection.tuple()
    c.execute("update posts set ext = ? where id = ?", (ext, post_id))
    conn.commit()
    conn.close()


def edit_post_privacy(post_id: int, privacy: str) -> None:
    connection = get_conn()
    conn, c = connection.tuple()
    c.execute("update posts set privacy = ? where id = ?", (privacy, post_id))
    conn.commit()
    conn.close()


def get_next_post(current: str) -> Post | None:
    connection = get_conn()
    conn, c = connection.tuple()
    c.execute("select * from posts where name = ?", (current,))
    row = c.fetchone()

    if not row:
        conn.close()
        return None

    post = make_post(dict(row))

    c.execute(
        "select * from posts p join users u on p.user = u.id where u.lister = 1 and p.date < ? and privacy = 'public' order by p.date desc limit 1",
        (post.date,),
    )

    row = c.fetchone()
    conn.close()

    if row:
        return make_post(dict(row))

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
    mage: bool = True,
    user_id: int | None = None,
) -> int | None:
    if (not username) or (not password):
        return None

    connection = get_conn()
    conn, c = connection.tuple()
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
        mage,
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
        "mage",
    ]

    if mode == "add":
        values.extend([date, date])
        columns.extend(["register_date", "last_date"])
        placeholders = ", ".join(["?"] * len(values))
        query = f"insert into users ({', '.join(columns)}) values ({placeholders}) returning id"
        c.execute(query, values)
        user_id = c.fetchone()[0]
    elif mode == "edit":
        values.append(user_id)
        clause = ", ".join([f"{col} = ?" for col in columns])
        query = f"update users set {clause} where id = ?"
        c.execute(query, values)
    else:
        return None

    conn.commit()
    conn.close()
    return user_id


def make_user(row: dict[str, Any]) -> User:
    return User(
        id=int(row.get("id") or 0),
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
        mage=bool(row.get("mage")),
    )


def get_users(
    user_id: int | None = None,
    username: str | None = None,
    oconn: Connection | None = None,
) -> list[User]:
    connection = get_conn(oconn)
    conn, c = connection.tuple()

    if user_id:
        c.execute("select * from users where id = ?", (user_id,))
        rows = [c.fetchone()]
    elif username:
        c.execute("select * from users where username = ?", (username,))
        rows = [c.fetchone()]
    else:
        c.execute("select * from users")
        rows = c.fetchall()

    users = []
    rows = [row for row in rows if row]

    for row in rows:
        user = make_user(dict(row))
        user.num_posts = get_post_count(user.id, oconn=connection)
        user.num_reactions = get_reaction_count(user_id=user.id, oconn=connection)
        users.append(user)

    if not oconn:
        conn.close()

    return users


def delete_user(user_id: int) -> None:
    connection = get_conn()
    conn, c = connection.tuple()
    c.execute("delete from users where id = ?", (user_id,))
    conn.commit()
    conn.close()


def delete_normal_users() -> None:
    connection = get_conn()
    conn, c = connection.tuple()
    query = "delete from users where admin != 1"
    c.execute(query)
    conn.commit()
    conn.close()


def mod_user(ids: list[int], what: str, value: Any) -> None:
    connection = get_conn()
    conn, c = connection.tuple()
    placeholders = ", ".join("?" for _ in ids)
    query = f"update users set {what} = ? where id in ({placeholders})"
    c.execute(query, (value, *ids))
    conn.commit()
    conn.close()


def update_user_last_date(user_id: int) -> None:
    connection = get_conn()
    conn, c = connection.tuple()
    c.execute("update users set last_date = ? where id = ?", (utils.now(), user_id))
    conn.commit()
    conn.close()


def get_random_post(ignore_ids: list[int]) -> Post | None:
    connection = get_conn()
    conn, c = connection.tuple()
    query = "select * from posts p join users u on p.user = u.id where p.id not in ({}) and u.lister = 1 order by random() limit 1"
    placeholders = ", ".join("?" for _ in ignore_ids)
    c.execute(query.format(placeholders), ignore_ids)
    row = c.fetchone()
    conn.close()

    if row:
        return make_post(dict(row))

    return None


def update_file_size(name: str, size: int) -> None:
    connection = get_conn()
    conn, c = connection.tuple()
    c.execute("update posts set size = ? where name = ?", (size, name))
    conn.commit()
    conn.close()


def add_reaction(post_id: int, user_id: int, value: str) -> int | None:
    connection = get_conn()
    conn, c = connection.tuple()
    cols = ["post", "user", "value", "date"]
    placeholders = ", ".join("?" for _ in cols)

    c.execute(
        f"insert into reactions ({','.join(cols)}) values ({placeholders}) returning id",
        (post_id, user_id, value, utils.now()),
    )

    reaction_id = c.fetchone()[0]
    conn.commit()
    conn.close()
    return int(reaction_id) if reaction_id is not None else None


def make_reaction(row: dict[str, Any]) -> Reaction:
    return Reaction(
        id=int(row.get("id") or 0),
        post=int(row.get("post") or 0),
        user=int(row.get("user") or 0),
        value=row.get("value") or "",
        date=int(row.get("date") or 0),
    )


def get_reactions(
    reaction_id: int | None = None,
    post_id: int | None = None,
    user_id: int | None = None,
    post: Post | None = None,
    extra: bool = True,
    oconn: Connection | None = None,
) -> list[Reaction]:
    connection = get_conn(oconn)
    conn, c = connection.tuple()

    if reaction_id:
        c.execute("select * from reactions where id = ?", (reaction_id,))
        rows = [c.fetchone()]
    elif post_id:
        c.execute(
            "select * from reactions where post = ?",
            (post_id,),
        )

        rows = c.fetchall()
    elif user_id:
        c.execute(
            "select * from reactions where user = ?",
            (user_id,),
        )

        rows = c.fetchall()
    else:
        c.execute("select * from reactions")
        rows = c.fetchall()

    reactions = []
    rows = [row for row in rows if row]

    for row in rows:
        reaction = make_reaction(dict(row))

        if extra:
            if post:
                rpost = post
            else:
                rpost = None

            ruser = None

            if not rpost:
                rposts = get_posts(post_id=reaction.post, extra=False, oconn=connection)
                rpost = rposts[0] if rposts else None

            if rpost:
                reaction.parent = rpost
            else:
                reaction.parent = None

            if not ruser:
                rusers = get_users(user_id=reaction.user, oconn=connection)
                ruser = rusers[0] if rusers else None

            if ruser:
                reaction.author = ruser
            else:
                reaction.author = None

        reactions.append(reaction)

    if not oconn:
        conn.close()

    return reactions


def get_reaction_count(
    post_id: int | None = None,
    user_id: int | None = None,
    oconn: Connection | None = None,
) -> int:
    connection = get_conn(oconn)
    conn, c = connection.tuple()

    if post_id and user_id:
        c.execute(
            "select count(*) from reactions where post = ? and user = ?",
            (
                post_id,
                user_id,
            ),
        )
    elif user_id:
        c.execute(
            "select count(*) from reactions where user = ?",
            (user_id,),
        )
    elif post_id:
        c.execute("select count(*) from reactions where post = ?", (post_id,))
    else:
        c.execute("select count(*) from reactions")

    result = c.fetchone()
    count = result[0] if result is not None else 0

    if not oconn:
        conn.close()

    return count


def get_last_reaction(post_id: int, oconn: Connection | None = None) -> Reaction | None:
    connection = get_conn(oconn)
    conn, c = connection.tuple()

    c.execute(
        "select * from reactions where post = ? order by date desc limit 1", (post_id,)
    )

    row = c.fetchone()

    if not oconn:
        conn.close()

    if row:
        return make_reaction(dict(row))

    return None


def get_post_count(user_id: int | None = None, oconn: Connection | None = None) -> int:
    connection = get_conn(oconn)
    conn, c = connection.tuple()
    c.execute("select count(*) from posts where user = ?", (user_id,))
    result = c.fetchone()
    count = result[0] if result is not None else 0

    if not oconn:
        conn.close()

    return count


def get_latest_post() -> Post | None:
    connection = get_conn()
    conn, c = connection.tuple()
    c.execute("select * from posts where privacy = 'public' order by date desc limit 1")
    row = c.fetchone()
    conn.close()

    if row:
        return make_post(dict(row))

    return None


def delete_reaction(reaction_id: int) -> None:
    connection = get_conn()
    conn, c = connection.tuple()
    c.execute("delete from reactions where id = ?", (reaction_id,))
    conn.commit()
    conn.close()


def delete_all_posts() -> None:
    connection = get_conn()
    conn, c = connection.tuple()
    c.execute("delete from posts")
    conn.commit()
    conn.close()


def delete_all_reactions() -> None:
    connection = get_conn()
    conn, c = connection.tuple()
    c.execute("delete from reactions")
    conn.commit()
    conn.close()


def edit_reaction(reaction_id: int, value: str) -> None:
    connection = get_conn()
    conn, c = connection.tuple()

    c.execute(
        "update reactions set value = ? where id = ?",
        (value, reaction_id),
    )

    conn.commit()
    conn.close()


def username_exists(username: str) -> bool:
    connection = get_conn()
    conn, c = connection.tuple()
    c.execute("select username from users where username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result is not None
