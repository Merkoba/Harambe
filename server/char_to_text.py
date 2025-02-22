import database


def update_reaction_modes() -> None:
    conn, c = database.get_conn()
    c.execute("update reactions set mode = 'text' where mode = 'character'")
    conn.commit()
    conn.close()


update_reaction_modes()
