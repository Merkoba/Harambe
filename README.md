![](screenshot.png)

This is a simple file uploader that is configurable and has an admin page.

It's made entirely in python using flask.

---

## Installation

Make a virtual env and install requirements.

Read [this](#config) to see how to configure it.

Run with gunicorn with this systemd service:

```
[Unit]
Description=Gunicorn instance to serve harambe
After=network.target

[Service]
User=someuser
Group=www-data
WorkingDirectory=/home/someuser/harambe/server
ExecStart=/home/someuser/harambe/server/venv/bin/python -m gunicorn -w 4 "app:app" --bind 0.0.0.0:4040
TimeoutStopSec=3

[Install]
WantedBy=multi-user.target
```

In apache conf:

```
ProxyPreserveHost On
ProxyPass / http://localhost:4040/
ProxyPassReverse / http://localhost:4040/
```

---

## Config <a name="config"></a>

Configs are set in `server/config.toml` which you must create.

You can check the default values in [config.py](server/config.py) and redefine what you need.

The `toml` format looks as followed:

For example:

```toml
captcha_length = 8

files_dir = "/mnt/drive/harambe"

uppercase_ids = false

# These must go at the bottom or it might not parse correctly:

[[users]]
username = "ronald"
password = "bigmac"

[[users]]
username = "admiral"
password = "tokyo1993"

[[keys]]
name = "seabird"
limit = 10

[[keys]]
name = "orbit"
limit = 6
id = "orb"
```

The config file is automatically reloaded when the file is modified.

This is done by using the `watchdog` library.

So there's no need to restart the server on config changes.

There are some exceptions like `app_key` or the captcha settings which can't be changed at runtime.

---

## Admin

There is an admin page to view and delete files:

![](admin.png)

Each admin looks like this:

```toml
[[admins]]
username = "johnnycage"
password = "goroballs"
```

---

## Users

Users can upload directly from the command line.

And it might be necesary to supply one in the web interface if `require_key` is enabled.

Their files can be signed if they have a `name` property.

Each user looks likes this:

```toml
[[users]]
key = "wingwalker"
name = "The Upsetter"
limit = 20
max = 20
```

`key` is a string which should be kept secret, it's what is used to authenticate.

`name` is the public name to be displayed in posts.

If `name` is empty, no name will be displayed.

`max` is the max file size for that key.

If `max` is set to 0 it will use the default max file size config.

---

## Style

The main image at the top can be replaced by creating a file in `server/static/img`.

This file is called `banner` and it can be `jpg`, `png`, or `gif`.

It's also possible to change the `background_color` and `font_family`.

As well as `accent_color`, `font_color`, `text_color`, and `link_color`.

---

## List

A file index page can be enabled with `list_enabled`.

This will allow anybody to view the list of uploaded files.

This is turned off by default.

The list can be slightly protected with a password.

This is a word that is needed to be included in the URL.

This is sent as the `pw` GET parameter.

For example `site.com/list?pw=bigdrop`

If `list_password` is `bigdrop`.

---

## Links

Links can be show in the main page if you create them in the config:

```toml
[[links]]
name = "About"
url = "/page/about"
target = "_blank"
```

`target` is optional. `_blank` means to open them in a new tab.

---

## Assets

There is a directory called `assets` inside `static`.

This directoy is not version controlled so you can add anything you want.

You can use this to host html pages which you can link in the main page.

Just make sure to not delete the `.gitignore` file that is inside.

---

## Database

There is an `sqlite3` database that holds some data about the files.

This includes the creation date, the title, and views.

This is all handled automatically.

This is located in `server/database.sqlite3`.