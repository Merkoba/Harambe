from __future__ import annotations

# Standard
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from config import Config


def fill(config: Config) -> None:
    fill_icons(config)
    fill_media_icons(config)


def fill_icons(config: Config) -> None:
    # Icon for posts
    config.icons["posts"] = "😎"

    # Icon for reactions
    config.icons["reactions"] = "🫠"

    # Icon for users
    config.icons["users"] = "🤪"

    # Icon for public posts
    config.icons["public"] = "🌎"

    # Icon for private posts
    config.icons["private"] = "🔒"

    # Icon for fresh posts
    config.icons["fresh"] = "🐟"

    # Icon for random
    config.icons["random"] = "🎲"

    # Icon for upload
    config.icons["upload"] = "💾"

    # Icon for menu
    config.icons["menu"] = "🧭"

    # Icon for edit
    config.icons["edit"] = "📝"

    # Icon for delete
    config.icons["delete"] = "💣"

    # Icon for deleted
    config.icons["deleted"] = "👻"

    # Icon for logout
    config.icons["logout"] = "🪂"

    # Icon for asc
    config.icons["asc"] = "📈"

    # Icon for desc
    config.icons["desc"] = "📉"

    # Icon for filename
    config.icons["filename"] = "💾"

    # Icon for settings
    config.icons["settings"] = "🎨"

    # Icon for page
    config.icons["page"] = "📟"

    # Icon for refresh
    config.icons["refresh"] = "🔃"

    # Icon for search
    config.icons["search"] = "🔍"

    # Icon for prev sample button
    config.icons["prev_sample"] = "⏪"

    # Icon for next sample button
    config.icons["next_sample"] = "⏩"

    # Icon for volume
    config.icons["volume"] = "🔊"

    # Icon for volume max
    config.icons["volume_max"] = "🔊"

    # Icon for volume mid
    config.icons["volume_mid"] = "🔉"

    # Icon for volume min
    config.icons["volume_min"] = "🔈"

    # Icon for volume mute
    config.icons["volume_muted"] = "🔇"

    # Icon for confirm: ok
    config.icons["confirm_yes"] = "✅"

    # Icon for confirm: cancel
    config.icons["confirm_no"] = "❌"

    # Icon for list
    config.icons["list"] = "📚"

    # Icon for admin
    config.icons["admin"] = "📚"

    # Icon for links
    config.icons["links"] = "🔗"

    # Icon for you
    config.icons["you"] = "😸"

    # Icon for jump
    config.icons["jump"] = "⏫"

    # Icon for rewind
    config.icons["rewind"] = "⏪"

    # Icon for slow
    config.icons["slow"] = "🐢"

    # Icon for fast
    config.icons["fast"] = "🐇"

    # Icon for fade in
    config.icons["fade_in"] = "🌅"

    # Icon for fade out
    config.icons["fade_out"] = "🌇"

    # Icon for read
    config.icons["read"] = "📖"

    # Icon for download
    config.icons["download"] = "📥"

    # Icon for speed
    config.icons["speed"] = "🚅"

    # Icon for pitch
    config.icons["pitch"] = "🎹"

    # Icon for up
    config.icons["up"] = "⬆️"

    # Icon for down
    config.icons["down"] = "⬇️"

    # Icon for reset
    config.icons["reset"] = "🔄"

    # Icon for reverb
    config.icons["reverb"] = "🌊"

    # Icon for bass
    config.icons["bass"] = "🎸"

    # Icon for cut
    config.icons["cut"] = "✂️"

    # Icon for clockwise
    config.icons["clockwise"] = "🔃"

    # Icon for counterclockwise
    config.icons["counterclockwise"] = "🔄"

    # Icon for login
    config.icons["login"] = "🔐"

    # Icon for register
    config.icons["register"] = "📝"


def fill_media_icons(config: Config) -> None:
    # Sample icon for admin pages
    config.media_icons["any"] = "🪧"

    # Sample icon for videos
    config.media_icons["video"] = "📺"

    # Sample icon for images
    config.media_icons["image"] = "🖼️"

    # Sample icon for audio
    config.media_icons["audio"] = "🔊"

    # Sample icon for text
    config.media_icons["text"] = "📝"

    # Sample icon for zip
    config.media_icons["zip"] = "📦"

    # Sample icon for markdown
    config.media_icons["markdown"] = "🧑🏼‍🎨"

    # Sample icon for flash
    config.media_icons["flash"] = "💥"

    # Sample icon for talk
    config.media_icons["talk"] = "💬"

    # Sample icon for URL
    config.media_icons["url"] = "🔗"
