# Standard
import sys

# Libraries
from werkzeug.security import generate_password_hash as hashpass  # type: ignore

# Modules
import database


if len(sys.argv) < 3:
    sys.exit(1)

username = sys.argv[1]
password = sys.argv[2]

if (not username) or (not password):
    sys.exit(1)

database.add_user("add", username, hashpass(password), admin=True)
