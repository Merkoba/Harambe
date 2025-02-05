from __future__ import annotations

# Standard
import json
import string
from pathlib import Path


rate_limit = 12
rate_limit_change = 3

captcha_key = "change_me_with_file"
captcha_key_file = Path("captcha_key.txt")
captcha_cheat_file = Path("captcha_cheat.txt")
captcha_cheat = ""

text_mtype = "text/plain"
file_name_max = 12

max_file_size = 100_000_000
max_file_size_file = Path("max_file_size.txt")

code = "change_me_with_file"
code_file = Path("code.txt")

if captcha_key_file.is_file():
    with captcha_key_file.open("r") as f:
        captcha_key = f.read().strip()

if captcha_cheat_file.is_file():
    with captcha_cheat_file.open("r") as f:
        captcha_cheat = f.read().strip()

if code_file.is_file():
    with code_file.open("r") as f:
        code = f.read().strip()

if max_file_size_file.is_file():
    with max_file_size_file.open("r") as f:
        max_file_size = int(f.read().strip()) * 1_000_000

captcha = {
    "SECRET_CAPTCHA_KEY": captcha_key,
    "CAPTCHA_LENGTH": 10,
    "CAPTCHA_DIGITS": False,
    "EXPIRE_SECONDS": 60,
    "CAPTCHA_IMG_FORMAT": "JPEG",
    "ONLY_UPPERCASE": False,
    "CHARACTER_POOL": string.ascii_lowercase,
}
