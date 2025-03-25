from __future__ import annotations

# Standard
import copy
import tomllib
import time
import threading
from pathlib import Path
from dataclasses import dataclass
from typing import Any

# Libraries
from watchdog.observers import Observer  # type: ignore
from watchdog.events import FileSystemEventHandler  # type: ignore

# Modules
import utils


class FileChangeHandler(FileSystemEventHandler):  # type: ignore
    def __init__(self, config: Config) -> None:
        self.path = config.path

    def on_modified(self, event: Any) -> None:
        if Path(event.src_path) == self.path:
            config.read()


@dataclass
class Link:
    name: str
    url: str
    icon: str = ""
    target: str = "_self"


class Config:
    def __init__(self, main: bool = True) -> None:
        self.reference: Config | None

        if main:
            self.reference = Config(False)
        else:
            self.reference = None

        self.path: Path = Path("config.toml")

        # List of links to show in the index page
        # Dict object: name, url, target (optional)
        self.links: list[Link] = [
            Link("About", "/static/demo/about.html", "🛟"),
            Link("Memorial", "/static/demo/memorial.html", "🦍"),
        ]

        # Secret key for security
        # Make it a long random string
        self.app_key: str = "fixthis"

        # The location to save the files
        # It can be outside the project folder
        self.files_dir: str = "files"

        # The location for video samplenail files
        # It can be outside the project folder
        self.samples_dir: str = "samples"

        # Default max size for users
        # You can admin them per case later
        # Low value in case public reigster is on
        self.max_size_user: int = 20

        # Port for the redis server
        # Redis is used for the limiter
        self.redis_port: int = 6379

        # Uppercase the post names
        # This is used to name the files
        self.uppercase_names: bool = False

        # Maximum number of posts to keep stored
        # After this the older posts will be deleted
        # The files are also deleted
        self.max_posts: int = 10_000

        # Maximum storage in GB
        # After this the older posts will be deleted
        self.max_storage: int = 10

        # Show the image in the web interface
        self.show_image: bool = True

        # Default page size for the admin page
        self.admin_page_size: int = 50

        # Length of the post name
        # Minimum is 10, maximum is 26
        self.post_name_length: int = 10

        # Requests per minute limit for most endpoints
        self.rate_limit: int = 60

        # Background color for the web interface
        self.background_color: str = "81, 81, 81"

        # Accent color for the web interface
        self.accent_color: str = "127, 104, 164"

        # Text color for the web interface
        self.text_color: str = "255, 255, 255"

        # Link color for the web interface
        self.link_color: str = "222, 211, 239"

        # Alt color for some text elements
        self.alt_color: str = "193, 234, 178"

        # Font family for the web interface
        self.font_family: str = "sans-serif"

        # Maximum age for the files cache on the user's side
        # Keep this is a huge number to avoid reloading
        # Or a low number to force file reload more often
        self.max_age: int = 31536000

        # Show the max file size in the web interface
        self.show_max_size: bool = True

        # Enable a public page to list posts
        self.list_enabled: bool = True

        # List is private and requires being logged in
        self.list_private: bool = True

        # Default page size for the list page
        self.list_page_size: int = 50

        # Maximum posts allowed to be shown in the list page
        # If 0 it will allow showing all posts
        self.list_max_posts: int = 100

        # Maximum reactions allowed to be shown in the list page
        # If 0 it will allow showing all reactions
        self.list_max_reactions: int = 100

        # Allow admins to delete posts using the admin page or endpoints
        self.allow_delete: bool = True

        # The title of the main index page
        self.main_title: str = "Harambe"

        # Tooltip message to show on the main image
        self.image_tooltip: str = ""

        # The first part of image urls
        # For example 'file' in site.com/file/abc123.jpg
        self.file_path: str = "file"

        # Maximum length allowed for titles
        self.max_title_length: int = 280

        # Allow titles on post uploads
        self.allow_titles: bool = True

        # Enable uploads through the web interface
        self.web_uploads_enabled: bool = True

        # Enable uploads through the API
        self.api_upload_enabled: bool = True

        # The endpoint for api uploads for your scripts
        # This should be relatively secret
        self.api_upload_endpoint = "apiupload"

        # Max size in megabytes to consider files for media embeds
        # Make it 0 to allow any size
        self.embed_max_size_image: int = 100
        self.embed_max_size_video: int = 100
        self.embed_max_size_audio: int = 100
        self.embed_max_size_flash: int = 100
        self.embed_max_size_text: int = 100
        self.embed_max_size_markdown: int = 100

        # Users can edit their own posts
        self.allow_edit: bool = True

        # Allow or block media hotlinking
        self.allow_hotlinks: bool = True

        # Default requests per minute for uploads
        self.requests_per_minute = 5

        # Allow non-users to view posts and files
        self.public_posts: bool = True

        # Don't increment view if last view is within this delay in seconds
        self.view_delay: int = 1

        # Content of the description meta tag in the index
        self.description_upload: str = "Ask Harambe for your file to be uploaded"

        # Content of the description meta tag in posts
        self.description_post: str = "File kindly uploaded by Harambe"

        # Allow reactions in posts
        self.reactions_enabled = True

        # Max length for text reactions
        self.max_reaction_length = 2000

        # Max reactions a user can do
        self.max_user_reactions = 20

        # Max reactions allowed on a post
        self.post_reaction_limit = 250

        # Seconds interval to refresh post pages
        self.post_refresh_interval = 30

        # The number of times to refresh posts before stopping
        self.post_refresh_times = 30

        # Allow users to edit their name
        self.allow_name_edit = True

        # Allow users to change their password
        self.allow_password_edit = True

        # Font size for all pages
        self.font_size = 20

        # Font size for the admin pages
        self.admin_font_size = 18

        # Max length for user username
        self.max_user_username_length = 240

        # Max length for user password
        self.max_user_password_length = 240

        # Max length for user name
        self.max_user_name_length = 30

        # Register page will be enabled
        self.register_enabled = True

        # The max displayed length of names in posts
        self.max_post_name_length = 18

        # The max displayed length of names in reactions
        self.max_reaction_name_length = 18

        # The compression level for zip files
        # 1 is the fastest, 9 is the strongest
        self.zip_level = 9

        # Allow files with the same hash
        self.allow_same_hash = False

        # Max number of files to be uploaded at the same time
        self.max_upload_files = 20

        # Generate and use samples
        self.samples_enabled = True

        # Width of samples
        self.sample_width = 1280

        # Height of samples
        self.sample_height = 720

        # Background color for samples
        self.sample_color = "black"

        # Compression quality for the jpg images
        # 2-31, lower is better quality
        self.sample_quality_image = 6

        # Compression quality for audio samples
        # 0-9, lower is better quality
        self.sample_quality_audio = 2

        # Max number of bytes to save for text files
        self.sample_text_bytes = 5_000

        # Max chars for zip samples
        self.sample_zip_chars = 1000

        # Lifetime of a user login session in days
        self.session_days = 365 * 5

        # Sample icon for admin pages
        self.sample_icon = "🔊"

        # Icon for prev sample button
        self.prev_sample_icon = "⏪"

        # Icon for next sample button
        self.next_sample_icon = "⏩"

        # Max length for post marks
        self.max_mark_length = 20

        # Image quality for image magic
        # 1-31, where 1 is best
        self.image_magic_quality = 8

        # Minimum file size to apply image magic
        # If 0 it will apply to any file size
        self.image_magic_min_size = 0

        # Enable or disable image magic
        self.image_magic_enabled = True

        # Quality for audio magic mp3
        # 0 is the highest VBR quality
        self.audio_magic_quality = 0

        # Enable or disable audio magic
        self.audio_magic_enabled = True

        # Minimum file size to apply audio magic
        # If 0 it will apply to any file size
        self.audio_magic_min_size = 0

        # Quality for video magic mp3
        # Lower quality, faster encoding
        # Higher = lower quality
        self.video_magic_quality = 28

        # Quality for video magic audio
        # 0 is the highest VBR quality
        self.video_magic_audio_quality = 0

        # Enable or disable video magic
        self.video_magic_enabled = True

        # Minimum file size to apply video magic
        # If 0 it will apply to any file size
        self.video_magic_min_size = 0

        # Quality for album magic mp3
        # 0 is the highest VBR quality
        self.album_magic_quality = 0

        # Enable or disable album magic
        self.album_magic_enabled = True

        # Quality for album magic mp3
        # 0 is the highest VBR quality
        self.visual_magic_audio_quality = 0

        # Width for audio album magic
        self.visual_magic_width = 1920

        # Height for audio album magic
        self.visual_magic_height = 1080

        # Quality for album magic video
        # Lower quality, faster encoding
        # Higher = lower quality
        self.visual_magic_video_quality = 28

        # Background color for visual magic
        self.visual_magic_color = "black"

        # Enable or disable album magic
        self.visual_magic_enabled = True

        # Enable or disable gif magic
        self.gif_magic_enabled = True

        # Width for gif magic
        self.gif_magic_width = 640

        # Height for gif magic
        self.gif_magic_height = 480

        # Frames per second for gif magic
        self.gif_magic_fps = 1.5

        # Background color for gif magic
        self.gif_magic_color = "black"

        # Enable all kinds of magic
        self.magic_enabled = True

        # Show privacy options in the web interface
        self.show_privacy_select = True

        # Quality of album magic quality
        self.album_magic_quality = 0

        # New users get the 'mage' permission by default
        self.default_mage = False

        # A code needed for registration
        # If empty string, no code is needed
        self.register_code = ""

        # Used to fill 'original' from title when empty
        # Used in post_procs.py
        self.original_title_length = 30

        # Show menu icons
        self.show_menu_icons = True

        # Icon for posts
        self.icon_for_posts = "😎"

        # Icon for reactions
        self.icon_for_reactions = "🫠"

        # Icon for users
        self.icon_for_users = "🤪"

        # Icon for public posts
        self.icon_for_public = "🌎"

        # Icon for private posts
        self.icon_for_private = "🔒"

        # Icon for fresh posts
        self.icon_for_fresh = "🐟"

        # Icon for random
        self.icon_for_random = "🎲"

        # Icon for upload
        self.icon_for_upload = "🦍"

        # Icon for edit
        self.icon_for_edit = "📝"

        # Icon for delete
        self.icon_for_delete = "💣"

        # Icon for deleted
        self.icon_for_deleted = "👻"

        # Icon for logout
        self.icon_for_logout = "🪂"

        # Icon for asc
        self.icon_for_asc = "📈"

        # Icon for desc
        self.icon_for_desc = "📉"

        # Max captcha time
        self.max_captcha_time = 180

        # Enable captcha for registration
        self.captcha_enabled = True

        # Enable the pastebin feature
        self.pastebin_enabled = True

        # Max length for text uploads
        self.max_pastebin_length = 100_000

        # Max url length when making url files
        self.max_url_length = 1_000

        # Key for the YouTube API
        self.youtube_key = ""

        # Fetch title and thumbnail from YouTube
        self.fetch_youtube = True

        # Fetch URL for title
        self.fetch_url = True

        # Allow descriptions in the web interface
        self.allow_descriptions = True

        # Max length for descriptions
        self.max_description_length = 10_000

    # --- Methods ---

    def get_max_storage(self) -> int:
        return self.max_storage * 1_000_000_000

    def get_post_name_length(self) -> int:
        return max(min(self.post_name_length, 26), 10)

    def read(self) -> None:
        def defvalue(name: str) -> Any:
            return copy.deepcopy(getattr(self.reference, name))

        def set_value(c: dict[str, Any], name: str) -> None:
            setattr(self, name, c.get(name, defvalue(name)))

        with self.path.open("rb") as f:
            try:
                c = tomllib.load(f)
            except Exception as e:
                utils.error(e)
                return

            # Get all instance attributes that don't start with underscore and aren't methods/properties
            config_attrs = [
                attr
                for attr in dir(self)
                if not attr.startswith("_")
                and not callable(getattr(self, attr))
                and attr not in ("links", "reference", "path")
            ]

            # Automatically set values for all config attributes
            for attr in config_attrs:
                set_value(c, attr)

            # Links
            links: list[dict[str, str]] = c.get("links", [])

            if links:
                self.links = [
                    Link(link["name"], link["url"], link.get("target", "_self"))
                    for link in links
                ]


# Fill it later
config = Config()


def start_observer() -> None:
    event_handler = FileChangeHandler(config)
    observer = Observer()
    observer.schedule(event_handler, path=str(config.path.parent), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# Fill the config object
config.read()

# Start the observer to check for config file changes
# This makes it possible to change things without restarting the server
observer_thread = threading.Thread(target=start_observer, daemon=True)
observer_thread.start()
