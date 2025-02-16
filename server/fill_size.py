# Standard
from pathlib import Path

# Modules
import database
from config import config


# Run this when you want to fill the database with the size of the files
# In case you don't have the size information in the database


path = config.files_dir
all_files = Path(path).glob("*")

for file in all_files:
    if file.is_file():
        size = file.stat().st_size
        print(f"{file.stem} - {size}")  # noqa
        database.update_file_size(file.stem, size)
