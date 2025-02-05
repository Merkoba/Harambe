from __future__ import annotations

# Standard
import tomllib
import string
from pathlib import Path


rate_limit = 12

text_mtype = "text/plain"
file_name_max = 12
admin_max_files = 1000

with Path("config.toml").open("rb") as f:
    config = tomllib.load(f)
    captcha_key = config["captcha_key"]
    captcha_cheat = config["captcha_cheat"]
    captcha_length = int(config["captcha_length"])
    codes = config["codes"]
    password = config["password"]
    max_file_size = int(config["max_file_size"]) * 1_000_000
    redis_port = config["redis_port"]

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
