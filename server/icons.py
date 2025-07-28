from __future__ import annotations

# Standard
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from config import Config


def fill(config: Config):
    fill_icons_1(config)
    fill_icons_2(config)


def fill_icons_1(config: Config):
    # Sample icon for admin pages
    config.sample_icon = "🪧"

    # Sample icon for videos
    config.sample_icon_video = "📺"

    # Sample icon for images
    config.sample_icon_image = "🖼️"

    # Sample icon for audio
    config.sample_icon_audio = "🔊"

    # Sample icon for text
    config.sample_icon_text = "📝"

    # Sample icon for zip
    config.sample_icon_zip = "📦"

    # Sample icon for markdown
    config.sample_icon_markdown = "🧑🏼‍🎨"

    # Sample icon for flash
    config.sample_icon_flash = "💥"

    # Sample icon for talk
    config.sample_icon_talk = "💬"

    # Sample icon for URL
    config.sample_icon_url = "🔗"

    # Icon for prev sample button
    config.prev_sample_icon = "⏪"

    # Icon for next sample button
    config.next_sample_icon = "⏩"


def fill_icons_2(config: Config):
    # Icon for posts
    config.icon_for_posts = "😎"

    # Icon for reactions
    config.icon_for_reactions = "🫠"

    # Icon for users
    config.icon_for_users = "🤪"

    # Icon for public posts
    config.icon_for_public = "🌎"

    # Icon for private posts
    config.icon_for_private = "🔒"

    # Icon for fresh posts
    config.icon_for_fresh = "🐟"

    # Icon for random
    config.icon_for_random = "🎲"

    # Icon for upload
    config.icon_for_upload = "💾"

    # Icon for menu
    config.icon_for_menu = "🧭"

    # Icon for edit
    config.icon_for_edit = "📝"

    # Icon for text
    config.icon_for_text = "📝"

    # Icon for image
    config.icon_for_image = "🖼️"

    # Icon for video
    config.icon_for_video = "📺"

    # Icon for audio
    config.icon_for_audio = "🔊"

    # Icon for talk
    config.icon_for_talk = "💬"

    # Icon for zip
    config.icon_for_zip = "📦"

    # Icon for flash
    config.icon_for_flash = "💥"

    # Icon for URL
    config.icon_for_url = "🔗"

    # Icon for delete
    config.icon_for_delete = "💣"

    # Icon for deleted
    config.icon_for_deleted = "👻"

    # Icon for logout
    config.icon_for_logout = "🪂"

    # Icon for asc
    config.icon_for_asc = "📈"

    # Icon for desc
    config.icon_for_desc = "📉"

    # Icon for filename
    config.icon_for_filename = "💾"

    # Icon for settings
    config.icon_for_settings = "🎨"

    # Icon for page
    config.icon_for_page = "📟"

    # Icon for refresh
    config.icon_for_refresh = "🔃"

    # Icon for search
    config.icon_for_search = "🔍"