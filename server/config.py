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
    def __init__(self, path: str) -> None:
        self.path = path

    def on_modified(self, event: Any) -> None:
        if event.src_path == self.path:
            read_config()


@dataclass
class Config:
    app_key: str = "fixthis"
    files_dir: str = "files"
    require_captcha: bool = True
    captcha: dict[str, Any] = field(default_factory=dict)
    captcha_key: str = ""
    captcha_cheat: str = ""
    captcha_length: int = 8
    password: str = "fixthis"
    max_file_size: int = 100
    redis_port: int = 6379
    require_key: bool = False
    key_limit: int = 3
    text_mtype: str = "text/plain"
    admin_max_files: int = 1000
    keys: list[str] = field(default_factory=list)
    uppercase_ids: bool = False
    extra_unique_ids: bool = False

    def get_max_file_size(self) -> int:
        return self.max_file_size * 1_000_000


# Used for default values
def_config = Config()

# Fill it later
config = Config()

# Path to the config file
configpath = Path("config/config.toml")


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
        set_value(c, "password")
        set_value(c, "max_file_size")
        set_value(c, "redis_port")
        set_value(c, "require_key")
        set_value(c, "key_limit")
        set_value(c, "uppercase_ids")
        set_value(c, "extra_unique_ids")
        set_value(c, "keys")

        config.captcha = {
            "SECRET_CAPTCHA_KEY": config.captcha_key or "nothing",
            "CAPTCHA_LENGTH": config.captcha_length,
            "CAPTCHA_DIGITS": False,
            "EXPIRE_SECONDS": 60,
            "CAPTCHA_IMG_FORMAT": "JPEG",
            "ONLY_UPPERCASE": False,
            "CHARACTER_POOL": string.ascii_lowercase,
        }


def start_observer() -> None:
    event_handler = FileChangeHandler(str(configpath))
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
