import database


def make_database() -> None:
    tables = ["posts", "users", "reactions"]
    conn, c = database.get_conn()

    for table in tables:
        # Create a temporary table with the new schema
        new_schema = ", ".join(
            [f"{col} {type}" for col, type in database.schemas[table].items()]
        )
        c.execute(f"CREATE TABLE IF NOT EXISTS {table}_new ({new_schema})")

        # Copy data from the old table to the new table
        if table == "reactions":
            columns = ", ".join([col for col in database.schemas[table].keys()])
            c.execute(
                f"INSERT INTO {table}_new ({columns}) SELECT {columns} FROM {table}"
            )
        else:
            old_columns = ", ".join(
                [col for col in database.schemas[table].keys() if col != "id"]
            )
            new_columns = ", ".join([col for col in database.schemas[table].keys()])
            c.execute(
                f"INSERT INTO {table}_new ({new_columns}) SELECT NULL, {old_columns} FROM {table}"
            )

        # Drop the old table
        c.execute(f"DROP TABLE {table}")

        # Rename the new table to the old table's name
        c.execute(f"ALTER TABLE {table}_new RENAME TO {table}")

    conn.commit()
    conn.close()


make_database()
