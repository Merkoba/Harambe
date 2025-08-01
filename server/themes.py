from __future__ import annotations

# Standard
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from config import Config


def fill(config: Config) -> None:
    themes_dir = Path(__file__).parent / "themes"
    theme_files = sorted(themes_dir.glob("*.toml"))

    for theme_path in theme_files:
        key = theme_path.stem

        try:
            with open(theme_path, "rb") as f:
                theme_data = tomllib.load(f)
                config.themes[key] = theme_data
        except Exception as e:
            print(f"Warning: Could not load theme file {theme_path.name}: {e}")
