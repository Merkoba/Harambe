def migrate_files_to_posts() -> None:
    conn, c = database.get_conn()

    # Check if the 'files' table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='files'")
    if c.fetchone():
        # Copy data from 'files' to 'posts'
        c.execute("""
            INSERT INTO posts (name, ext, date, title, views, original, username, uploader, mtype, view_date, listed, size, sample)
            SELECT name, ext, date, title, views, original, username, uploader, mtype, view_date, listed, size, sample
            FROM files
        """)
        conn.commit()

    conn.close()

# Call the migration function
migrate_files_to_posts()