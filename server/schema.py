# Standard
import re

# Modules
import database


schemas = {
    "posts": {
        "name": "text primary key default ''",
        "ext": "text default ''",
        "date": "integer default 0",
        "title": "text default ''",
        "views": "integer default 0",
        "original": "text default ''",
        "username": "text default ''",
        "mtype": "text default ''",
        "view_date": "integer default 0",
        "listed": "integer default 1",
        "size": "integer default 0",
        "sample": "text default ''",
    },
    "reactions": {
        "id": "integer primary key autoincrement",
        "post": "text default ''",
        "user": "text default ''",
        "value": "text default ''",
        "mode": "text default ''",
        "listed": "int default 1",
        "date": "int default 0",
    },
    "users": {
        "username": "text primary key default ''",
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


# Create tables or fill missing values
def make_database() -> None:
    tables = ["posts", "users", "reactions"]
    conn, c = database.get_conn()

    for table in tables:
        c.execute(f"create table if not exists {table} ({get_schema(table)})")

    def add_columns(what: str) -> None:
        c.execute(f"pragma table_info({what})")
        columns = [info[1] for info in c.fetchall()]
        schema = schemas[what]

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

    for table in tables:
        add_columns(table)

    conn.commit()
    conn.close()


make_database()
