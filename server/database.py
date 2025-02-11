from __future__ import annotations

# Standard
import sys
from pathlib import Path
from typing import Any
import json

# Modules
import utils
import log


class File:
    def __init__(self, name: str, date: int, size: int, comment: str) -> None:
        self.id = Path(name).stem
        self.name = name
        self.date = date
        self.size = size
        self.comment = comment

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "date": self.date,
            "size": self.size,
            "comment": self.comment,
        }


class Database:
    def __init__(self) -> None:
        self.path: Path = Path("database.json")
        self.files: list[File] = []

    def generate(self) -> None:
        utils.log("Generating new database file...")
        files = utils.files_dir().glob("*")
        self.path.touch()
        self.files = []

        for file in files:
            if file.is_file():
                name = file.name
                date = int(file.stat().st_ctime)
                size = int(file.stat().st_size)
                f = File(name, date, size, "")
                self.files.append(f)

        self.sort()
        self.save()

    def load(self) -> None:
        try:
            if not self.path.exists():
                self.generate()
                return

            with self.path.open() as file:
                content = file.read().strip()

                if not content:
                    self.generate()
                    return

                obj = json.loads(content)

                for f in obj["files"]:
                    name = f["name"]
                    date = f["date"]
                    size = f["size"]
                    comment = f.get("comment", "")
                    self.files.append(File(name, date, size, comment))
        except Exception as e:
            utils.error(e)
            sys.exit(1)

    def sort(self) -> None:
        self.files.sort(key=lambda x: x.date, reverse=False)

    def add_file(self, name: str, size: int, comment: str) -> File:
        log.info("add file")
        self.files = list(filter(lambda x: x.name != name, self.files))
        file = File(name, utils.now(), size, comment)
        self.files.append(file)
        self.save()
        return file

    def remove_file(self, name: str) -> None:
        for file in self.files:
            if file.name == name:
                self.files.remove(file)
                self.save()
                return

    def get_file(self, id_: str) -> File | None:
        log.info("getfile")
        for file in self.files:
            if file.id == id_:
                log.info("found")
                return file

        log.info("notfound")
        return None

    def save(self) -> None:
        obj = {"files": [f.to_dict() for f in self.files]}

        with self.path.open("w") as file:
            file.write(json.dumps(obj, indent=4))


database = Database()
database.load()
