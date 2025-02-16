# Standard
import re

# Modules
import database


# Posts

schema_posts = {
    "name": "text primary key default ''",
    "ext": "text default ''",
    "date": "integer default 0",
    "title": "text default ''",
    "views": "integer default 0",
    "original": "text default ''",
    "username": "text default ''",
    "uploader": "text default ''",
    "mtype": "text default ''",
    "view_date": "integer default 0",
    "listed": "integer default 1",
    "size": "integer default 0",
    "sample": "text default ''",
    "reactions": "text default ''",
}


# Users

schema_users = {
    "username": "text primary key default ''",
    "password": "text default ''",
    "admin": "integer default 0",
    "name": "text default ''",
    "rpm": "integer default 0",
    "max_size": "integer default 0",
    "can_list": "integer default 1",
    "mark": "text default ''",
    "register_date": "integer default 0",
    "last_date": "integer default 0",
    "lister": "integer default 1",
    "posts": "integer default 0",
    "reacter": "integer default 1",
}


def get_schema(what: str) -> str:
    if what == "posts":
        sch = schema_posts
    elif what == "users":
        sch = schema_users
    else:
        sch = {}

    return ",".join([f"{k} {v}" for k, v in sch.items()]).strip()


# Create tables or fill missing values
def make_database() -> None:
    conn, c = database.get_conn()

    c.execute(f"create table if not exists posts ({get_schema('posts')})")
    c.execute(f"create table if not exists users ({get_schema('users')})")

    def add_columns(what: str) -> None:
        c.execute(f"pragma table_info({what})")
        columns = [info[1] for info in c.fetchall()]

        if what == "posts":
            schema = schema_posts
        elif what == "users":
            schema = schema_users
        else:
            print("Invalid table")  # noqa
            return

        for column, c_type in schema.items():
            if column not in columns:
                c.execute(f"alter table {what} add column {column} {c_type}")
            else:
                match = re.search(r"default\s+(\d+)", c_type)

                if match:
                    defvalue = match.group(1)
                    c.execute(
                        f"update {what} set {column} = {defvalue} where {column} is null"
                    )

    add_columns("posts")
    add_columns("users")

    conn.commit()
    conn.close()


make_database()
