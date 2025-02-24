import sys
import database
import user_procs


# I decided to not use incremental int ids on the 'posts' and 'users' tables.
# I prefer linking tables with usernames for simplicity and speed.
# Changeability is not a big issue because users have the 'name' property.
# However in case the username has to be changed, there is this script.


def feedback(s: str) -> None:
    print(s)  # noqa


if len(sys.argv) != 3:
    feedback("Usage: change_username.py <old_username> <new_username>")
    exit(1)


old_username = sys.argv[1]
new_username = sys.argv[2]
ok, _ = user_procs.check_value(None, "username", new_username)


if (not old_username) or (not new_username):
    feedback("Please provide both the old and new usernames.")
    exit(1)


if not ok:
    feedback("Invalid new username.")
    exit(1)


if not database.username_exists(old_username):
    feedback("Old username does not exist.")
    exit(1)


if database.username_exists(new_username):
    feedback("New username already exists.")
    exit(1)


database.change_username(old_username, new_username)
feedback("Username changed successfully.")
