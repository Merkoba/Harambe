# Modules
import database


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
    "admin": "integer",
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
        sch = {}

    return ",".join([f"{k} {v}" for k, v in sch.items()]).strip()


# Create tables or fill missing values
def make_database() -> None:
    conn, c = database.get_conn()

    c.execute(f"create table if not exists files ({get_schema('files')})")
    c.execute(f"create table if not exists users ({get_schema('users')})")

    def add_columns(what: str) -> None:
        c.execute(f"pragma table_info({what})")
        columns = [info[1] for info in c.fetchall()]

        if what == "files":
            schema = schema_files
        elif what == "users":
            schema = schema_users
        else:
            print("Invalid table")  # noqa
            return

        for column, c_type in schema.items():
            if column not in columns:
                c.execute(f"alter table {what} add column {column} {c_type}")

    add_columns("files")
    add_columns("users")

    conn.commit()
    conn.close()


make_database()
