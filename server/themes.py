from __future__ import annotations

# Standard
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from config import Config


def fill(config: Config) -> None:
    fill_theme_1(config)
    fill_theme_2(config)
    fill_theme_3(config)
    fill_theme_4(config)
    fill_theme_5(config)
    fill_theme_6(config)
    fill_theme_7(config)
    fill_theme_8(config)
    fill_theme_9(config)
    fill_theme_10(config)


def fill_theme_1(config: Config) -> None:
    config.themes["blossom"] = {
        "name": "Steel Blossom",
        "colors": {
            "background_color": "81, 81, 81",
            "accent_color": "127, 104, 164",
            "accent_color_text": "255, 255, 255",
            "text_color": "255, 255, 255",
            "link_color": "222, 211, 239",
            "alt_color": "193, 234, 178",
            "button_background_color_1": "69, 156, 198",
            "button_background_color_2": "93, 104, 80",
            "button_background_color_3": "129, 147, 108",
            "button_text_color": "255, 255, 255",
        },
    }


def fill_theme_2(config: Config) -> None:
    config.themes["ocean"] = {
        "name": "Ocean Deep",
        "colors": {
            "background_color": "25, 39, 52",
            "accent_color": "70, 130, 180",
            "accent_color_text": "255, 255, 255",
            "text_color": "240, 248, 255",
            "link_color": "135, 206, 250",
            "alt_color": "64, 224, 208",
            "button_background_color_1": "30, 144, 255",
            "button_background_color_2": "72, 61, 139",
            "button_background_color_3": "100, 149, 237",
            "button_text_color": "255, 255, 255",
        },
    }


def fill_theme_3(config: Config) -> None:
    config.themes["forest"] = {
        "name": "Forest Night",
        "colors": {
            "background_color": "34, 49, 34",
            "accent_color": "85, 139, 47",
            "accent_color_text": "255, 255, 255",
            "text_color": "245, 255, 250",
            "link_color": "144, 238, 144",
            "alt_color": "255, 215, 0",
            "button_background_color_1": "34, 139, 34",
            "button_background_color_2": "107, 142, 35",
            "button_background_color_3": "154, 205, 50",
            "button_text_color": "255, 255, 255",
        },
    }


def fill_theme_4(config: Config) -> None:
    config.themes["sunset"] = {
        "name": "Sunset Glow",
        "colors": {
            "background_color": "54, 34, 24",
            "accent_color": "255, 69, 0",
            "accent_color_text": "255, 255, 255",
            "text_color": "255, 248, 220",
            "link_color": "255, 140, 0",
            "alt_color": "255, 215, 0",
            "button_background_color_1": "205, 85, 65",
            "button_background_color_2": "210, 115, 25",
            "button_background_color_3": "200, 130, 35",
            "button_text_color": "255, 255, 255",
        },
    }


def fill_theme_5(config: Config) -> None:
    config.themes["purple"] = {
        "name": "Purple Haze",
        "colors": {
            "background_color": "45, 25, 55",
            "accent_color": "147, 112, 219",
            "accent_color_text": "255, 255, 255",
            "text_color": "248, 248, 255",
            "link_color": "186, 85, 211",
            "alt_color": "255, 20, 147",
            "button_background_color_1": "138, 43, 226",
            "button_background_color_2": "75, 0, 130",
            "button_background_color_3": "106, 90, 205",
            "button_text_color": "255, 255, 255",
        },
    }


def fill_theme_6(config: Config) -> None:
    config.themes["arctic"] = {
        "name": "Arctic Ice",
        "colors": {
            "background_color": "248, 252, 255",
            "accent_color": "70, 130, 180",
            "accent_color_text": "255, 255, 255",
            "text_color": "25, 25, 112",
            "link_color": "0, 100, 200",
            "alt_color": "0, 191, 255",
            "button_background_color_1": "65, 105, 225",
            "button_background_color_2": "30, 144, 255",
            "button_background_color_3": "135, 206, 250",
            "button_text_color": "255, 255, 255",
        },
    }


def fill_theme_7(config: Config) -> None:
    config.themes["golden"] = {
        "name": "Golden Sand",
        "colors": {
            "background_color": "255, 253, 240",
            "accent_color": "184, 134, 11",
            "accent_color_text": "255, 255, 255",
            "text_color": "101, 63, 13",
            "link_color": "146, 64, 14",
            "alt_color": "34, 139, 34",
            "button_background_color_1": "218, 165, 32",
            "button_background_color_2": "205, 133, 63",
            "button_background_color_3": "210, 180, 140",
            "button_text_color": "119, 59, 12",
        },
    }


def fill_theme_8(config: Config) -> None:
    config.themes["midnight"] = {
        "name": "Midnight Black",
        "colors": {
            "background_color": "18, 18, 18",
            "accent_color": "220, 220, 220",
            "accent_color_text": "0, 0, 0",
            "text_color": "240, 240, 240",
            "link_color": "173, 216, 230",
            "alt_color": "255, 105, 180",
            "button_background_color_1": "105, 105, 105",
            "button_background_color_2": "128, 128, 128",
            "button_background_color_3": "169, 169, 169",
            "button_text_color": "255, 255, 255",
        },
    }


def fill_theme_9(config: Config) -> None:
    config.themes["neon"] = {
        "name": "Cyber Neon",
        "colors": {
            "background_color": "12, 12, 12",
            "accent_color": "0, 255, 127",
            "accent_color_text": "0, 0, 0",
            "text_color": "0, 255, 0",
            "link_color": "0, 255, 255",
            "alt_color": "255, 0, 255",
            "button_background_color_1": "0, 240, 240",
            "button_background_color_2": "88, 230, 212",
            "button_background_color_3": "90, 225, 50",
            "button_text_color": "0, 0, 0",
        },
    }


def fill_theme_10(config: Config) -> None:
    config.themes["sepia"] = {
        "name": "Sepia Classic",
        "colors": {
            "background_color": "112, 82, 60",
            "accent_color": "205, 133, 63",
            "accent_color_text": "255, 255, 255",
            "text_color": "255, 248, 220",
            "link_color": "222, 184, 135",
            "alt_color": "240, 230, 140",
            "button_background_color_1": "149, 79, 29",
            "button_background_color_2": "160, 82, 45",
            "button_background_color_3": "205, 133, 63",
            "button_text_color": "255, 255, 255",
        },
    }
