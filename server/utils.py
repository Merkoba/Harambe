# Standard
import time
import random
from pathlib import Path

# Modules
import config


def now() -> float:
    return time.time()


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


def get_size(n: int) -> float:
    return round(n / 1_000_000, 2)


def singular_or_plural(num: float, singular: str, plural: str) -> str:
    if num == 1:
        return singular

    return plural


def time_ago(start_time: float, end_time: float) -> str:
    diff = end_time - start_time
    seconds = int(diff)

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


def error(e: Exception) -> None:
    print(e)  # noqa
