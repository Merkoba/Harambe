import sys
import database
import user_procs


# I decided to not use incremental int ids on the 'posts' and 'users' tables.
# I prefer linking tables with usernames for simplicity and speed.
# Changeability is not a big issue because users have the 'name' property.
# However in case the username has to be changed, there is this script.


if len(sys.argv) != 3:
    print("Usage: change_username.py <old_username> <new_username>")
    exit(1)


old_username = sys.argv[1]
new_username = sys.argv[2]
ok, _ = user_procs.check_value(None, "username", new_username)


if (not old_username) or (not new_username):
    print("Please provide both the old and new usernames")
    exit(1)


if not ok:
    print("Invalid new username")
    exit(1)


if not database.username_exists(old_username):
    print("Old username does not exist")
    exit(1)


if database.username_exists(new_username):
    print("New username already exists")
    exit(1)


database.change_username(old_username, new_username)
print("Username changed successfully")