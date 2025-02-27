import sqlite3
import database
import utils
from pathlib import Path

Path("database.sqlite3").touch()

conn = sqlite3.connect("database_old.sqlite3")
conn.row_factory = sqlite3.Row
c = conn.cursor()

conn2 = sqlite3.connect("database.sqlite3")
conn2.row_factory = sqlite3.Row
c2 = conn2.cursor()

c.execute("SELECT * FROM posts")
posts = c.fetchall()

c.execute("SELECT * FROM reactions")
reactions = c.fetchall()

c.execute("SELECT * FROM users")
users = c.fetchall()

for post in posts:
    c.execute("SELECT * FROM users WHERE username = ?", (post["username"],))
    user = c.fetchone()
    c2.execute(
        "INSERT INTO posts (id, name, ext, date, title, views, original, mtype, view_date, listed, size, sample, user) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            post["id"],
            post["name"],
            post["ext"],
            post["date"],
            post["title"],
            post["views"],
            post["original"],
            post["mtype"],
            post["view_date"],
            post["listed"],
            post["size"],
            post["sample"],
            user["id"],
        ),
    )
    conn2.commit()

for reaction in reactions:
    c.execute("SELECT * FROM users WHERE username = ?", (reaction["user"],))
    user = c.fetchone()
    c.execute("SELECT * FROM posts WHERE name = ?", (reaction["post"],))
    post = c.fetchone()

    if (not user) or (not post):
        utils.q("User or post not found")
        continue

    c2.execute(
        "INSERT INTO reactions (id, value, mode, listed, date, post, user) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            reaction["id"],
            reaction["value"],
            reaction["mode"],
            reaction["listed"],
            reaction["date"],
            post["id"],
            user["id"],
        ),
    )
    conn2.commit()

for user in users:
    c2.execute(
        "INSERT INTO users (id, username, password, admin, name, rpm, max_size, reader, mark, register_date, last_date, lister, poster, reacter) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            user["id"],
            user["username"],
            user["password"],
            user["admin"],
            user["name"],
            user["rpm"],
            user["max_size"],
            user["reader"],
            user["mark"],
            user["register_date"],
            user["last_date"],
            user["lister"],
            user["poster"],
            user["reacter"],
        ),
    )
    conn2.commit()
