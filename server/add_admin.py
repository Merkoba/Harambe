# Standard
import sys

# Modules
import database


if len(sys.argv) < 3:
    sys.exit(1)

database.add_user("add", sys.argv[1], sys.argv[2], admin=True)
print("Done")  # noqa
