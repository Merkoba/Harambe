from __future__ import annotations

# Standard
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from config import Config


def fill(config: Config) -> None:
    themes_dir = Path(__file__).parent / "themes"

    themes = [
        "blossom",
        "ocean",
        "forest",
        "sunset",
        "purple",
        "arctic",
        "golden",
        "midnight",
        "neon",
        "sepia",
        "crimson",
        "pastel",
        "teal",
        "cherry",
        "mocha",
        "contrast",
    ]

    for key in themes:
        theme_path = themes_dir / f"{key}.toml"

        if theme_path.exists():
            with open(theme_path, "rb") as f:
                theme_data = tomllib.load(f)
                config.themes[key] = theme_data
        else:
            print(f"Warning: Theme file {filename} not found")
