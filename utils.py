# Standard
import time
import random


def now() -> float:
    return time.time()


def numstring(n: int) -> str:
    return "".join([str(random.randint(0, 9)) for _ in range(n)])


def file_name(name: str, max: int) -> str:
    name = "".join([c for c in name if c.isalnum() or c in "_-"])
    name = name[:max]

    while name and (not name[-1].isalnum()):
        name = name[:-1]

    return name or "file"