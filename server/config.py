from __future__ import annotations

# Standard
import copy
import tomllib
import string
import time
import threading
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

# Libraries
from watchdog.observers import Observer  # type: ignore
from watchdog.events import FileSystemEventHandler  # type: ignore


class FileChangeHandler(FileSystemEventHandler):  # type: ignore
    def __init__(self, path: Path) -> None:
        self.path = path

    def on_modified(self, event: Any) -> None:
        if Path(event.src_path) == self.path:
            read_config()


@dataclass
class User:
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password


@dataclass
class Key:
    def __init__(self, name: str, limit: int, id_: str = "") -> None:
        self.name = name
        self.limit = limit
        self.id = id_


@dataclass
class Config:
    # Users that can use the admin page
    # Dict object: username, password
    users: list[User] = field(default_factory=list)

    # Keys that can be used to upload files
    # Dict object: name, limit, id (optional)
    keys: list[Key] = field(default_factory=list)

    # Secret key for security
    # Make it a long random string
    app_key: str = "fixthis"

    # The location to save the files
    # It can be outside the project folder
    files_dir: str = "files"

    # Require to solve a captcha to upload in the web interface
    require_captcha: bool = True

    # Secret key for security
    # Make it a long random string
    captcha_key: str = ""

    # Use this to cheat the captcha
    # Should be kept semi-secret
    captcha_cheat: str = ""

    # Length of the captcha
    # The higher the number, the harder it is
    captcha_length: int = 8

    # Maximum file size in MB
    # File beyond this will get ignored
    max_file_size: int = 100

    # Port for the redis server
    # Redis is used for the limiter
    redis_port: int = 6379

    # Require to input a key to upload in the web interface
    require_key: bool = False

    # Uppercase the file ids
    # The id is used to name the files
    uppercase_ids: bool = False

    # Maximum number of files to keep stored
    # After this the older files will be deleted
    max_files: int = 10_000

    # Maximum storage in GB
    # After this the older files will be deleted
    max_storage: int = 10

    # Show the image in the web interface
    show_image: bool = True

    # Default page size for the admin page
    admin_page_size: int = 100

    # Length of the file name
    # Minimum is 10, maximum is 26
    file_name_length: int = 10

    # Requests per minute limit for most endpoints
    rate_limit: int = 20

    # Background color for the web interface
    background_color: str = "rgb(81 81 81)"

    # Accent color for the web interface
    accent_color: str = "rgb(127 104 164)"

    # Font color for the web interface
    font_color: str = "white"

    # Text color for the web interface
    text_color: str = "white"

    # Link color for the web interface
    link_color: str = "rgb(222 211 239)"

    # Font family for the web interface
    font_family: str = "sans-serif"

    # Maximum age for the files cache on the user's side
    # Keep this is a huge number to avoid reloading
    # Or a low number to force file reload more often
    max_age = 31536000

    # Show the max file size in the web interface
    show_max_file_size: bool = True

    # Enable a public page to list files
    enable_list: bool = False

    # Default page size for the list page
    list_page_size: int = 100

    # Require a special word in the URL to access the list page
    # For example: site.com/list?pw=palmtree
    # This is to make the list semi-private
    list_password: str = ""

    # Allow admins to delete files using the admin page or endpoints
    allow_delete: bool = True

    # --- Methods ---

    def get_max_file_size(self) -> int:
        return self.max_file_size * 1_000_000

    def get_max_storage(self) -> int:
        return self.max_storage * 1_000_000_000

    def get_file_name_length(self) -> int:
        return max(min(self.file_name_length, 26), 10)

    def check_user(self, username: str, password: str) -> bool:
        for user in self.users:
            if (user.username == username) and (user.password == password):
                return True

        return False

    def get_captcha(self) -> dict[str, Any]:
        return {
            "SECRET_CAPTCHA_KEY": self.captcha_key or "nothing",
            "CAPTCHA_LENGTH": self.captcha_length,
            "CAPTCHA_DIGITS": False,
            "EXPIRE_SECONDS": 60,
            "CAPTCHA_IMG_FORMAT": "JPEG",
            "ONLY_UPPERCASE": False,
            "CHARACTER_POOL": string.ascii_lowercase,
        }


# Used for default values
def_config = Config()

# Fill it later
config = Config()

# Path to the config file
configpath = Path("config.toml")


def defvalue(name: str) -> Any:
    return copy.deepcopy(getattr(def_config, name))


def read_config() -> None:
    def set_value(c: dict[str, Any], name: str) -> None:
        setattr(config, name, c.get(name, defvalue(name)))

    with configpath.open("rb") as f:
        c = tomllib.load(f)

        set_value(c, "app_key")
        set_value(c, "files_dir")
        set_value(c, "require_captcha")
        set_value(c, "captcha_key")
        set_value(c, "captcha_cheat")
        set_value(c, "captcha_length")
        set_value(c, "max_file_size")
        set_value(c, "redis_port")
        set_value(c, "require_key")
        set_value(c, "uppercase_ids")
        set_value(c, "max_files")
        set_value(c, "max_storage")
        set_value(c, "show_image")
        set_value(c, "admin_page_size")
        set_value(c, "file_name_length")
        set_value(c, "rate_limit")
        set_value(c, "background_color")
        set_value(c, "accent_color")
        set_value(c, "font_color")
        set_value(c, "text_color")
        set_value(c, "link_color")
        set_value(c, "font_family")
        set_value(c, "max_age")
        set_value(c, "show_max_file_size")
        set_value(c, "enable_list")
        set_value(c, "list_page_size")
        set_value(c, "list_password")
        set_value(c, "allow_delete")

        # Users

        users: list[dict[str, str]] = c.get("users", [])
        config.users = [User(user["username"], user["password"]) for user in users]

        # Keys

        keys: list[dict[str, Any]] = c.get("keys", [])

        config.keys = [
            Key(key["name"], key["limit"], key.get("id", "")) for key in keys
        ]


def start_observer() -> None:
    event_handler = FileChangeHandler(configpath)
    observer = Observer()
    observer.schedule(event_handler, path=str(configpath.parent), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# Fill the config object
read_config()

# Start the observer to check for config file changes
# This makes it possible to change things without restarting the server
observer_thread = threading.Thread(target=start_observer, daemon=True)
observer_thread.start()
