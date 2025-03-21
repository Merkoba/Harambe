from __future__ import annotations

# Standard
import re
import time
import json
import string
import random
import urllib.parse
import unicodedata
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

# Libraries
import redis  # type: ignore
import q as qlib  # type: ignore
from flask import jsonify, Request  # type: ignore

# Modules
from config import config
from post_procs import Post
from react_procs import Reaction
from user_procs import User


Items = list[Post] | list[Reaction] | list[User]


redis_client = redis.Redis()


TLDS = [
    "com",
    "org",
    "net",
    "io",
    "me",
    "tv",
    "gov",
    "edu",
    "info",
    "co",
]


def now() -> int:
    return int(time.time())


def numstring(n: int) -> str:
    return "".join([str(random_int(0, 9)) for _ in range(n)])


def file_name(name: str, max: int) -> str:
    name = "".join([c for c in name if c.isalnum() or c in "_-"])
    name = name[:max]

    while name and (not name[-1].isalnum()):
        name = name[:-1]

    while name and (not name[0].isalnum()):
        name = name[1:]

    return name or "file"


def get_size(n: int) -> str:
    if n < 1_000_000:
        return f"{round(n / 1_000, 2)} kb"

    if n < 1_000_000_000:
        return f"{round(n / 1_000_000, 2)} mb"

    return f"{round(n / 1_000_000_000, 2)} gb"


def singular_or_plural(num: float, singular: str, plural: str) -> str:
    if num == 1:
        return singular

    return plural


def time_ago(start_time: int, end_time: int) -> str:
    seconds = end_time - start_time

    if seconds < 5:
        return "Just now"

    if seconds < 60:
        word = singular_or_plural(seconds, "sec", "secs")
        return f"{seconds} {word} ago"

    minutes = seconds // 60

    if minutes < 60:
        word = singular_or_plural(minutes, "min", "mins")
        return f"{minutes} {word} ago"

    hours = minutes / 60

    if hours < 24:
        word = singular_or_plural(hours, "hr", "hrs")
        return f"{hours:.1f} {word} ago"

    days = hours / 24

    if days < 30:
        word = singular_or_plural(days, "day", "days")
        return f"{days:.1f} {word} ago"

    months = days / 30

    if months < 12:
        word = singular_or_plural(months, "month", "months")
        return f"{months:.1f} {word} ago"

    years = months / 12

    if years < 10:
        word = singular_or_plural(years, "year", "years")
        return f"{years:.1f} {word} ago"

    decades = years / 10

    if decades < 10:
        word = singular_or_plural(decades, "decade", "decades")
        return f"{decades:.1f} {word} ago"

    centuries = decades / 10

    if centuries < 10:
        word = singular_or_plural(centuries, "century", "centuries")
        return f"{centuries:.1f} {word} ago"

    millennia = centuries / 10
    word = singular_or_plural(millennia, "millennium", "millennia")
    return f"{millennia:.1f} {word} ago"


def files_dir() -> Path:
    return Path(config.files_dir)


def samples_dir() -> Path:
    return Path(config.samples_dir)


def log(s: str) -> None:
    q(s)


def error(e: Exception | str) -> None:
    q(e)


def get_dtime(date: int) -> datetime:
    return datetime.fromtimestamp(date)


def nice_date(date: int, mode: str = "full") -> str:
    dtime = get_dtime(date)

    if mode == "date":
        return dtime.strftime("%d %B %Y")

    if mode == "time":
        return dtime.strftime("%I:%M %p")

    return dtime.strftime("%d %B %Y | %I:%M %p")


def valid_file_name(name: str) -> bool:
    if not name:
        return False

    if name.startswith("."):
        return False

    if "/" in name:
        return False

    if "\\" in name:
        return False

    try:
        if not Path(name).stem:
            return False
    except Exception:
        return False

    return True


def clean_title(title: str) -> str:
    title = " ".join(title.split())
    return title[: config.max_title_length].strip()


def load_icons() -> list[str]:
    icons = [icon.stem for icon in Path("static/icons").glob("*.gif")]
    icons.sort()
    return icons


def single_line(s: str) -> str:
    return " ".join(s.split()).strip()


def q(*args: Any) -> None:
    qlib.q(args)


def count_graphemes(s: str) -> int:
    grapheme_count = 0

    i = 0
    while i < len(s):
        char = s[i]

        combining_class = unicodedata.combining(char)

        if combining_class == 0:
            grapheme_count += 1
            i += 1
        else:
            i += 1

            while i < len(s) and unicodedata.combining(s[i]) > 0:
                i += 1

    return grapheme_count


def clean_query(s: Any) -> str:
    return re.sub(r"[\s:]", "", str(s).lower())


def bad(message: str = "") -> tuple[str, int]:
    return jsonify({"status": "error", "message": message}), 400


def ok(message: str = "", data: dict[str, Any] | None = None) -> tuple[str, int]:
    data = data or {}
    return jsonify({"status": "ok", "message": message, **data}), 200


def contains_url(text: str) -> bool:
    if bool(re.search(r"(https?://|www\.)\S+", text, re.IGNORECASE)):
        return True

    pattern = r"\b\w+\.(" + "|".join(TLDS) + r")\b"
    return bool(re.search(pattern, text, re.IGNORECASE))


def remove_multiple_lines(text: str) -> str:
    return re.sub(r"\n\s*\n", "\n\n", text)


def space_string(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def check_dir(direc: str) -> bool:
    if not direc:
        return False

    if direc == "/":
        return False

    if direc == ".":
        return False

    if (direc == "~") or (direc == "~/"):
        return False

    return direc != "/home"


def get_banner() -> str:
    banners = list(Path("static/img/banners").glob("*"))
    return random.choice(banners).name


def clean_filename(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "", name)[:50].strip()


def decode(s: str) -> str:
    return str(urllib.parse.unquote(s))


def is_text_file(path: Path) -> bool:
    """Determine if a file is text by attempting to read it."""
    # Read first chunk of the file (e.g., 8KB)
    with path.open("rb") as f:
        chunk = f.read(8192)

    ok = False

    # Check for NULL bytes and other control characters that suggest binary data
    # NULL bytes are a strong indicator of binary content
    if b"\x00" in chunk:
        return False

    # Try to decode as UTF-8
    try:
        chunk.decode("utf-8")
        ok = True
    except UnicodeDecodeError:
        pass

    if ok:
        return True

    # Try to decode with other common encodings
    for encoding in ["latin-1", "iso-8859-1", "windows-1252"]:
        if try_decode(chunk, encoding):
            return True

    return ok


def try_decode(chunk: bytes, encoding: str) -> bool:
    try:
        chunk.decode(encoding)
    except UnicodeDecodeError:
        return False

    return True


def get_checkbox(request: Request, key: str) -> bool:
    return str(request.form.get(key, "off")) == "on"


def run_cmd(command: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        error(f"Error: {e.stderr.strip()}")
        raise


def do_sort(items: Items, sort: str, different: list[str]) -> None:
    split = sort.split("_")
    key = "_".join(split[0:-1])
    order = split[-1]
    reverse = key in different

    if order == "desc":
        reverse = not reverse

    items.sort(key=lambda x: getattr(x, key), reverse=reverse)


def random_int(min: int, max: int) -> int:
    return random.randint(min, max)


def random_letter() -> str:
    return random.choice(string.ascii_lowercase)


def random_string(n: int) -> str:
    return "".join(random_letter() for _ in range(n))


def get_captcha() -> tuple[str, str, str]:
    a = random_int(11, 99)
    b = random_int(11, 99)
    c = random_int(11, 99)

    n = now()
    answer = a * b * c
    question = f"What is {a} * {b} * {c}"
    key = f"captcha_{n}"
    div = random_string(random_int(6, 16))
    redis_save(key, {"answer": answer, "time": n}, config.max_captcha_time)
    return question, key, div


def redis_save(key: str, value: dict[str, Any], expire: int | None = None) -> None:
    s = json.dumps(value)

    if expire:
        redis_client.set(key, s, ex=expire)
    else:
        redis_client.set(key, s)


def redis_get(key: str) -> dict[str, Any]:
    value = redis_client.get(key)
    return json.loads(value) if value else {}


def redis_delete(key: str) -> None:
    redis_client.delete(key)


ICONS = load_icons()
