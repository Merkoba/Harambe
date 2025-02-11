# Standard
import time
import random
from datetime import datetime
from pathlib import Path

# Modules
from config import config


def now() -> datetime:
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


def nice_date(date: int) -> str:
    dtime = get_dtime(date)
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
        p = Path(name)

        if (not p.stem) or (not p.suffix):
            return False
    except Exception:
        return False

    return True
