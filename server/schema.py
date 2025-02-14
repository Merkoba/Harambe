# Standard
import sqlite3


db_path = "database.sqlite3"

schema_files = {
    "name": "text primary key",
    "ext": "text",
    "date": "integer",
    "title": "text",
    "views": "integer default 0",
    "original": "text",
    "username": "text",
    "uploader": "text",
    "mtype": "text",
}

schema_users = {
    "username": "text primary key",
    "password": "text",
    "name": "text",
    "rpm": "integer",
    "max_size": "integer",
    "can_list": "integer",
    "mark": "text",
    "register_date": "integer",
    "last_date": "integer",
}


def get_schema(what: str) -> str:
    if what == "files":
        sch = schema_files
    elif what == "users":
        sch = schema_users
    else:
        raise ValueError(f"Invalid schema: {what}")

    return ",".join([f"{k} {v}" for k, v in sch.items()]).strip()


def get_conn() -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    return conn, c


# Create tables or fill missing values
def make_database() -> None:
    conn, c = get_conn()

    c.execute(f"create table if not exists files ({get_schema("files")})")
    c.execute(f"create table if not exists users ({get_schema("users")})")

    def add_columns(what: str) -> None:
        c.execute(f"pragma table_info({what})")
        columns = [info[1] for info in c.fetchall()]

        if what == "files":
            schema = schema_files
        elif what == "users":
            schema = schema_users

        for column, c_type in schema.items():
            if column not in columns:
                utils.log(f"Adding column: {column}")
                c.execute(f"alter table files add column {column} {c_type}")

    add_columns("files")
    add_columns("users")

    conn.commit()
    conn.close()


make_database()