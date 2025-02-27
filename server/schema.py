# Standard
import re

# Modules
import database
import utils


# Create tables or fill missing values
def make_database() -> None:
    tables = ["posts", "users", "reactions"]
    conn, c = database.get_conn()

    for table in tables:
        c.execute(f"create table if not exists {table} ({database.get_schema(table)})")

    def add_columns(what: str) -> None:
        c.execute(f"pragma table_info({what})")
        columns = [info[1] for info in c.fetchall()]
        schema = database.schemas[what]

        for column, c_type in schema.items():
            if "foreign" in column:
                continue

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
