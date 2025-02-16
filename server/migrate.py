# Modules
import database


conn, c = database.get_conn()

c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='files'")

if c.fetchone():
    c.execute("""
        INSERT INTO posts
        SELECT * FROM files
    """)
    conn.commit()

conn.close()
