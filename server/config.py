from __future__ import annotations

# Standard
import copy
import tomllib
import string
import time
import threading
from pathlib import Path
from dataclasses import dataclass
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
class Admin:
    username: str
    password: str


@dataclass
class User:
    key: str
    name: str
    limit: int
    max: int
    list: bool


@dataclass
class Link:
    name: str
    url: str
    target: str = "_self"


class Config:
    def __init__(self, main: bool = True) -> None:
        self.reference: Config | None

        if main:
            self.reference = Config(False)
        else:
            self.reference = None

        self.path: Path = Path("config.toml")

        # Admins can use manage files
        # Dict object: username, password
        self.admins: list[Admin] = []

        # Users can upload files
        # Dict object: name, limit, id (optional)
        self.users: list[User] = []

        # List of links to show in the index page
        # Dict object: name, url, target (optional)
        self.links: list[Link] = [
            Link("about", "/static/demo/about.html", "_blank"),
        ]

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
        self.admin_page_size: int = 50

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

        # List is private and requires a password or key
        self.list_private: bool = True

        # Default page size for the list page
        self.list_page_size: int = 50

        # Maximum of files allowed to be shown in the list page
        # If 0 it will allow showing all files
        self.list_max_files: int = 100

        # Allow users to view the list by using their key
        self.users_can_list: bool = False

        # Allow admins to delete files using the admin page or endpoints
        self.allow_delete: bool = True

        # The title of the main index page
        self.main_title: str = "Harambe"

        # Tooltip message to show on the main image
        self.image_tooltip: str = ""

        # The first part of image urls
        # For example 'file' in site.com/file/abc123.jpg
        self.file_path: str = "file"

        # Maximum length allowed for titles
        self.max_title_length: int = 2000

        # Allow titles on file uploads
        self.allow_titles: bool = True

        # Enable uploads through the web interface
        self.web_uploads_enabled: bool = True

        # Enable uploads through the API
        self.api_uploads_enabled: bool = True

    # --- Methods ---

    def get_max_file_size(self) -> int:
        return self.max_file_size * 1_000_000

    def get_max_storage(self) -> int:
        return self.max_storage * 1_000_000_000

    def get_file_name_length(self) -> int:
        return max(min(self.file_name_length, 26), 10)

    def check_admin(self, username: str, password: str) -> bool:
        for admin in self.admins:
            if (admin.username == username) and (admin.password == password):
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

    def get_user(self, key: str) -> User | None:
        for user in self.users:
            if user.key == key:
                return user

        return None

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
            set_value(c, "list_private")
            set_value(c, "list_page_size")
            set_value(c, "list_max_files")
            set_value(c, "users_can_list")
            set_value(c, "allow_delete")
            set_value(c, "main_title")
            set_value(c, "image_tooltip")
            set_value(c, "file_path")
            set_value(c, "allow_titles")
            set_value(c, "web_uploads_enabled")
            set_value(c, "api_uploads_enabled")

            # Admins

            admins: list[dict[str, str]] = c.get("admins", [])

            if admins:
                self.admins = [
                    Admin(admin["username"], admin["password"]) for admin in admins
                ]

            # Users

            users: list[dict[str, Any]] = c.get("users", [])

            if users:
                self.users = [
                    User(
                        user["key"],
                        user.get("name", ""),
                        user.get("limit", 12),
                        user.get("max", 0),
                        user.get("list", False),
                    )
                    for user in users
                ]

            # Links

            links: list[dict[str, str]] = c.get("links", [])

            if links:
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
