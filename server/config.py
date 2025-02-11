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
    def __init__(self, config: Config) -> None:
        self.path = config.path

    def on_modified(self, event: Any) -> None:
        if Path(event.src_path) == self.path:
            config.read()


@dataclass
class User:
    username: str
    password: str


@dataclass
class Key:
    name: str
    limit: int
    id: str


@dataclass
class Link:
    name: str
    url: str
    target: str


class Config:
    def __init__(self, main: bool = True) -> None:
        self.reference: Config | None

        if main:
            self.reference = Config(False)
        else:
            self.reference = None

        self.path: Path = Path("config.toml")

        # Users that can use the admin page
        # Dict object: username, password
        self.users: list[User] = field(default_factory=list)

        # Keys that can be used to upload files
        # Dict object: name, limit, id (optional)
        self.keys: list[Key] = field(default_factory=list)

        # List of links to show in the index page
        # Dict object: name, url, target (optional)
        self.links: list[Link] = field(default_factory=list)

        # Secret key for security
        # Make it a long random string
        self.app_key: str = "fixthis"

        # The location to save the files
        # It can be outside the project folder
        self.files_dir: str = "files"

        # Require to solve a captcha to upload in the web interface
        self.require_captcha: bool = True

        # Secret key for security
        # Make it a long random string
        self.captcha_key: str = ""

        # Use this to cheat the captcha
        # Should be kept semi-secret
        self.captcha_cheat: str = ""

        # Length of the captcha
        # The higher the number, the harder it is
        self.captcha_length: int = 8

        # Maximum file size in MB
        # File beyond this will get ignored
        self.max_file_size: int = 100

        # Port for the redis server
        # Redis is used for the limiter
        self.redis_port: int = 6379

        # Require to input a key to upload in the web interface
        self.require_key: bool = False

        # Uppercase the file ids
        # The id is used to name the files
        self.uppercase_ids: bool = False

        # Maximum number of files to keep stored
        # After this the older files will be deleted
        self.max_files: int = 10_000

        # Maximum storage in GB
        # After this the older files will be deleted
        self.max_storage: int = 10

        # Show the image in the web interface
        self.show_image: bool = True

        # Default page size for the admin page
        self.admin_page_size: int = 100

        # Length of the file name
        # Minimum is 10, maximum is 26
        self.file_name_length: int = 10

        # Requests per minute limit for most endpoints
        self.rate_limit: int = 20

        # Background color for the web interface
        self.background_color: str = "rgb(81 81 81)"

        # Accent color for the web interface
        self.accent_color: str = "rgb(127 104 164)"

        # Font color for the web interface
        self.font_color: str = "white"

        # Text color for the web interface
        self.text_color: str = "white"

        # Link color for the web interface
        self.link_color: str = "rgb(222 211 239)"

        # Font family for the web interface
        self.font_family: str = "sans-serif"

        # Maximum age for the files cache on the user's side
        # Keep this is a huge number to avoid reloading
        # Or a low number to force file reload more often
        self.max_age: int = 31536000

        # Show the max file size in the web interface
        self.show_max_file_size: bool = True

        # Enable a public page to list files
        self.list_enabled: bool = False

        # Default page size for the list page
        self.list_page_size: int = 50

        # Maximum of files allowed to be shown in the list page
        # If 0 it will allow showing all files
        self.list_max_files: int = 100

        # Require a special word in the URL to access the list page
        # For example: site.com/list?pw=palmtree
        # This is to make the list semi-private
        self.list_password: str = ""

        # Allow admins to delete files using the admin page or endpoints
        self.allow_delete: bool = True

        # The title of the main index page
        self.main_title: str = "Upload"

        # Tooltip message to show on the main image
        self.image_tooltip: str = "Upload a file"

        # The first part of image urls
        # For example 'file' in site.com/file/abc123.jpg
        self.file_path: str = "file"

        # Maximum length allowed for comments
        self.max_comment_length: int = 500

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

    def read(self) -> None:
        def defvalue(name: str) -> Any:
            return copy.deepcopy(getattr(self.reference, name))

        def set_value(c: dict[str, Any], name: str) -> None:
            setattr(self, name, c.get(name, defvalue(name)))

        with self.path.open("rb") as f:
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
            set_value(c, "list_enabled")
            set_value(c, "list_page_size")
            set_value(c, "list_password")
            set_value(c, "list_max_files")
            set_value(c, "allow_delete")
            set_value(c, "main_title")
            set_value(c, "image_tooltip")
            set_value(c, "file_path")

            # Users

            users: list[dict[str, str]] = c.get("users", [])
            self.users = [User(user["username"], user["password"]) for user in users]

            # Keys

            keys: list[dict[str, Any]] = c.get("keys", [])

            self.keys = [
                Key(key["name"], key.get("limit", 12), key.get("id", ""))
                for key in keys
            ]

            # Links

            links: list[dict[str, str]] = c.get("links", [])

            self.links = [
                Link(link["name"], link["url"], link.get("target", "_self"))
                for link in links
            ]


# Fill it later
config = Config()


def start_observer() -> None:
    event_handler = FileChangeHandler(config)
    observer = Observer()
    observer.schedule(event_handler, path=str(config.path.parent), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# Fill the config object
config.read()

# Start the observer to check for config file changes
# This makes it possible to change things without restarting the server
observer_thread = threading.Thread(target=start_observer, daemon=True)
observer_thread.start()
