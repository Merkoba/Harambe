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
import mimetypes
import requests  # type: ignore
from datetime import datetime
from pathlib import Path
from typing import Any

# Libraries
import redis  # type: ignore
import q as qlib  # type: ignore
from flask import jsonify, Request  # type: ignore
from werkzeug.datastructures import FileStorage  # type: ignore
import libarchive  # type: ignore

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

archive_extensions = [
    ".zip",
    ".tar",
    ".tar.gz",
    ".tar.bz2",
    ".tar.xz",
    ".tar.lz",
    ".tar.Z",
    ".tgz",
    ".tbz2",
    ".txz",
    ".tlz",
    ".tZ",
    ".gz",
    ".bz2",
    ".xz",
    ".lz",
    ".7z",
    ".rar",
    ".cab",
    ".iso",
    ".lha",
    ".lzh",
    ".ar",
    ".deb",
    ".rpm",
    ".dmg",
    ".hfs",
    ".cpio",
    ".shar",
    ".pax",
    ".ustar",
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
    count = 0
    i = 0

    while i < len(s):
        char = s[i]
        combining = unicodedata.combining(char)

        if combining == 0:
            count += 1
            i += 1
        else:
            i += 1

            while (i < len(s)) and (unicodedata.combining(s[i]) > 0):
                i += 1

    return count


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


def ext_split(name: str) -> list[str]:
    return name.rsplit(".", 1)


def clean_full_filename(name: str) -> str:
    split = ext_split(name)

    if len(split) == 1:
        return clean_filename(split[0])

    stem, ext = split
    stem = clean_filename(stem)
    ext = clean_filename(ext).lower()

    if not ext:
        return stem

    return f"{stem}.{ext}"


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


def get_captcha() -> tuple[str, str]:
    a = random_int(11, 99)
    b = random_int(11, 99)
    c = random_int(11, 99)
    d = random_int(11, 99)

    n = now()
    answer = a * b * c * d
    question = f"{a} * {b} * {c} * {d}"
    key = f"captcha_{n}"
    redis_save(key, {"answer": answer, "time": n}, config.max_captcha_time)
    return question, key


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


def get_content_type(file: FileStorage) -> str:
    return file.content_type or mimetypes.guess_type(file.filename)[0] or ""


def is_media_file(what: str, file: FileStorage, ignore: list[str]) -> bool:
    ct = get_content_type(file)
    return ct.startswith(f"{what}/") and (not any(ct == f"{what}/{g}" for g in ignore))


def is_image_file(
    file: FileStorage, lossless: bool = False, ignore_gif: bool = False
) -> bool:
    if lossless:
        ignore = config.magic_image_ignore
    else:
        ignore = []

    if ignore_gif:
        ignore.append("gif")

    return is_media_file("image", file, ignore)


def is_audio_file(file: FileStorage, lossless: bool = False) -> bool:
    if lossless:
        ignore = config.magic_audio_ignore
    else:
        ignore = []

    return is_media_file("audio", file, ignore)


def is_video_file(file: FileStorage, lossless: bool = False) -> bool:
    if lossless:
        ignore = config.magic_video_ignore
    else:
        ignore = []

    return is_media_file("video", file, ignore)


def is_gif_file(file: FileStorage) -> bool:
    return is_media_file("gif", file, [])


def fix_filename(name: str) -> str:
    split = name.split(".")
    stem = clean_filename(".".join(split[:-1]))
    ext = split[-1].lower().strip()
    return f"{stem}.{ext}"


def get_youtube_id(url: str) -> list[Any] | None:
    split = re.split(r"(vi\/|v%3D|v=|\/v\/|youtu\.be\/|\/embed\/|\/live\/)", url)

    if len(split) > 2:
        id_part = re.split(r"[^0-9a-z_-]", split[2], flags=re.IGNORECASE)[0]
    else:
        id_part = split[0]

    v_id = id_part if len(id_part) == 11 else ""
    list_match = re.search(r"(?:\?|&)(list=[0-9A-Za-z_-]+)", url)
    index_match = re.search(r"(?:\?|&)(index=[0-9]+)", url)

    if list_match:
        list_id = list_match.group(1).replace("list=", "")
    else:
        list_id = ""

    if list_id and (not v_id):
        index = 0

        if index_match:
            index = int(index_match.group(1).replace("index=", "")) - 1

        return ["list", [list_id, index]]

    if v_id:
        return ["video", v_id]

    return None


def is_youtube_url(url: str) -> bool:
    return is_url(url) and bool(get_youtube_id(url))


def is_url(s: str, allow_space: bool = False) -> bool:
    if (not allow_space) and (" " in s):
        return False

    if len(s) > config.max_url_length:
        return False

    if any(prefix in s for prefix in ["https://", "http://"]):
        if len(s) <= (s.find("://") + 3):
            return False

        return not s.endswith(("]", "'", '"'))

    return False


def get_youtube_info(url: str) -> tuple[str, str, bytes | None] | None:
    if not config.youtube_key:
        return None

    yt_info = get_youtube_id(url)

    if not yt_info:
        return None

    if yt_info[0] != "video":
        return None

    vid = yt_info[1]

    try:
        key = config.youtube_key
        api_url = "https://www.googleapis.com/youtube/v3/videos"
        api_url = f"{api_url}?id={vid}&key={key}&part=snippet"
        response = requests.get(api_url, timeout=5)

        if response.status_code == 200:
            data = response.json()

            if data["items"]:
                snippet = data["items"][0]["snippet"]
                title = snippet.get("title", "")
                description = snippet.get("description", "")
                thumbnail: bytes | None = None
                thumbnails = snippet["thumbnails"]
                thumbnail_url = None

                for quality in ["maxres", "high", "medium", "default"]:
                    if quality in thumbnails:
                        thumbnail_url = thumbnails[quality]["url"]
                        break

                if thumbnail_url:
                    img_response = requests.get(thumbnail_url, timeout=5)

                    if img_response.status_code == 200:
                        thumbnail = img_response.content

                return title, description, thumbnail
        else:
            return None
    except Exception:
        return None

    return None


def get_url_info(url: str) -> tuple[str, str] | None:
    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            title = ""
            description = ""

            title_match = re.search(
                r"<title>(.*?)</title>", response.text, re.IGNORECASE
            )

            if title_match:
                title = title_match.group(1).strip()

            desc_match = re.search(
                r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']\s*/?>',
                response.text,
                re.IGNORECASE,
            )

            if not desc_match:
                desc_match = re.search(
                    r'<meta\s+content=["\'](.*?)["\']\s+name=["\']description["\']\s*/?>',
                    response.text,
                    re.IGNORECASE,
                )

            if desc_match:
                description = desc_match.group(1).strip()

            return title, description
    except Exception:
        pass

    return None


def clean_description(s: str) -> str:
    return untab_string(
        remove_multiple_lines(s)[: config.max_description_length].rstrip()
    )


def clean_pastebin(s: str) -> str:
    return untab_string(s[: config.max_pastebin_length].rstrip())


def do_query(obj: Post | Reaction | User, query: str, props: list[str]) -> bool:
    if not query:
        return True

    for prop in props:
        if query in clean_query(getattr(obj, prop)):
            return True

    return False


def untab_string(s: str) -> str:
    s = s.replace("\t", "  ")
    lines = s.split("\n")

    if len(lines) <= 1:
        return s

    ns = []
    pos = -1

    for line in lines:
        if not line.strip():
            continue

        m = re.match(r"^\s+", line)

        if m:
            n = len(m.group(0))

            if pos == -1 or n < pos:
                pos = n

            ns.append(n)
        else:
            return s

    new_lines = []
    spaces = " " * pos
    new_lines = [re.sub(f"^{spaces}", "", line) for line in lines]
    return "\n".join(new_lines)


def remove_metadata(path: Path) -> None:
    cmd = [
        "exiftool",
        "-all=",  # Remove all metadata
        "-tagsfromfile",
        "@",  # Copy tags from the original file
        "-orientation",  # Preserve orientation
        "-rotation",  # Preserve rotation
        "-overwrite_original",  # Don't create backup files
        str(path),
    ]

    run_cmd(cmd)


def striplimit(s: str, n: int) -> str:
    return s.strip()[:n].strip()


def shuffle(items: Items) -> None:
    random.shuffle(items)


def read_archive(
    source: str | Path | bytes, filename: str
) -> list[tuple[str, bytes, int]] | None:
    if not any(filename.endswith(ext) for ext in archive_extensions):
        return

    try:
        files_list: list[tuple[str, bytes, int]] = []

        # Try to open with libarchive
        if isinstance(source, bytes):
            # Handle bytes input
            with libarchive.memory_reader(source) as archive:
                for entry in archive:
                    if len(files_list) >= config.max_archive_files:
                        break

                    # Skip directories
                    if entry.isdir:
                        continue

                    filename = entry.name
                    file_size = entry.size

                    # Read file content
                    try:
                        file_content = b""

                        for block in entry.get_blocks():
                            file_content += block

                        files_list.append((filename, file_content, file_size))
                    except Exception:
                        # If we can't read the content, skip this file
                        continue
        else:
            # Handle file path input
            file_path = Path(source)

            # Check if file exists
            if not file_path.exists():
                return None

            with libarchive.file_reader(str(file_path)) as archive:
                for entry in archive:
                    if len(files_list) >= config.max_archive_files:
                        break

                    # Skip directories
                    if entry.isdir:
                        continue

                    filename = entry.name
                    file_size = entry.size

                    # Read file content
                    try:
                        file_content = b""
                        for block in entry.get_blocks():
                            file_content += block

                        files_list.append((filename, file_content, file_size))
                    except Exception:
                        # If we can't read the content, skip this file
                        continue

        return files_list if files_list else None

    except Exception as e:
        error(e)
        return None
