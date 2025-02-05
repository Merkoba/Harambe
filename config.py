from __future__ import annotations

# Standard
import tomllib
import string
from pathlib import Path


rate_limit = 12
rate_limit_change = 3

text_mtype = "text/plain"
file_name_max = 12
max_file_size = 100_000_000

with open(Path("config.toml"), "rb") as f:
    config = tomllib.load(f)
    captcha_key = config["captcha_key"]
    captcha_cheat = config["captcha_cheat"]
    code = config["code"]
    password = config["password"]
    max_file_size = int(config["max_file_size"]) * 1_000_000

captcha = {
    "SECRET_CAPTCHA_KEY": captcha_key,
    "CAPTCHA_LENGTH": 10,
    "CAPTCHA_DIGITS": False,
    "EXPIRE_SECONDS": 60,
    "CAPTCHA_IMG_FORMAT": "JPEG",
    "ONLY_UPPERCASE": False,
    "CHARACTER_POOL": string.ascii_lowercase,
}
