from __future__ import annotations

# Standard
import re
import time
import random
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

# Libraries
import q as qlib  # type: ignore
from flask import jsonify  # type: ignore

# Modules
from config import config


def now() -> int:
    return int(time.time())


def numstring(n: int) -> str:
    return "".join([str(random.randint(0, 9)) for _ in range(n)])


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
    word = singular_or_plural(years, "year", "years")
    return f"{years:.1f} {word} ago"


def files_dir() -> Path:
    return Path(config.files_dir)


def log(s: str) -> None:
    print(s)  # noqa


def error(e: Exception) -> None:
    print(e)  # noqa


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


def contains_url(text: str) -> list[str]:
    return re.findall(r"(https?://|www\.)\S+", text, re.IGNORECASE)


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


ICONS = load_icons()
