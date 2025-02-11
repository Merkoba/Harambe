# Standard
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
    path: Path = Path("database.json")
    files: dict[str, File] = {}

    def load(self) -> None:
        try:
            if not self.path.exists():
                self.path.touch()
                self.save()
                return

            with self.path.open() as file:
                content = file.read().strip()

                if not content:
                    self.save()
                    return

                obj = json.loads(content)

                for file in obj["files"]:
                    p = obj["files"][file]
                    self.files[file] = File(file, p["date"], p["size"])
        except Exception as e:
            utils.error(e)
            exit(1)

    def add_file(self, name: str, size: float) -> None:
        self.files[name] = File(name, utils.seconds(), size)
        self.save()

    def save(self) -> None:
        obj = {"files": {k: f.to_dict() for k, f in self.files.items()}}

        with self.path.open("w") as file:
            file.write(json.dumps(obj, indent=4))


database = Database()
database.load()
