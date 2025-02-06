from __future__ import annotations

# Standard
import tomllib
import string
from pathlib import Path


rate_limit = 12

text_mtype = "text/plain"
file_name_max = 12
admin_max_files = 1000

with Path("config/config.toml").open("rb") as f:
    config = tomllib.load(f)
    files_dir = config["files_dir"] or "files"
    captcha_key = config["captcha_key"] or ""
    captcha_cheat = config["captcha_cheat"] or ""
    captcha_length = int(config["captcha_length"] or 8)
    codes = config["codes"] or []
    password = config["password"] or "fixthis"
    max_file_size = int(config["max_file_size"] or 100) * 1_000_000
    redis_port = config["redis_port"] or 6379

captcha_enabled = bool(captcha_key)

captcha = {
    "SECRET_CAPTCHA_KEY": captcha_key or "nothing",
    "CAPTCHA_LENGTH": captcha_length,
    "CAPTCHA_DIGITS": False,
    "EXPIRE_SECONDS": 60,
    "CAPTCHA_IMG_FORMAT": "JPEG",
    "ONLY_UPPERCASE": False,
    "CHARACTER_POOL": string.ascii_lowercase,
}
