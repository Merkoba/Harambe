# Standard
import sys
from pathlib import Path
from typing import Any
import json

# Modules
import utils


class File:
    def __init__(self, name: str, date: int, size: float) -> None:
        self.name = name
        self.date = date
        self.size = size

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "date": self.date,
            "size": self.size,
        }


class Database:
    def __init__(self) -> None:
        self.path: Path = Path("database.json")
        self.files: dict[str, File] = {}

    def generate(self) -> None:
        utils.log("Generating new database file...")
        files = utils.files_dir().glob("*")
        self.path.touch()
        self.files = {}

        for file in files:
            if file.is_file():
                name = file.name
                date = int(file.stat().st_ctime)
                size = int(file.stat().st_size)
                self.files[file.name] = File(name, date, size)

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

                for key in obj["files"]:
                    p = obj["files"][key]
                    self.files[key] = File(key, p["date"], p["size"])
        except Exception as e:
            utils.error(e)
            sys.exit(1)

    def add_file(self, name: str, size: float) -> None:
        self.files[name] = File(name, utils.seconds(), size)
        self.save()

    def remove_file(self, name: str) -> None:
        self.files.pop(name)
        self.save()

    def save(self) -> None:
        obj = {"files": {k: f.to_dict() for k, f in self.files.items()}}

        with self.path.open("w") as file:
            file.write(json.dumps(obj, indent=4))


database = Database()
database.load()
