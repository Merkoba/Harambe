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
    app_key = config.get("app_key", "fixthis")
    files_dir = config.get("files_dir", "files")
    captcha_key = config.get("captcha_key", "")
    captcha_cheat = config.get("captcha_cheat", "")
    captcha_length = int(config.get("captcha_length", 8))
    codes = config.get("codes", [])
    password = config.get("password", "fixthis")
    max_file_size = int(config.get("max_file_size", 100))
    redis_port = config.get("redis_port", 6379)

max_file_size *= 1_000_000
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
