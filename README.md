![](screenshot.png)

This is a simple file uploader that is configurable and has an admin page.

It's made entirely in python using flask.

---

## Installation

Make a virtual env and install requirements.

Copy `config.toml.example` and make `config.toml`.

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

## Admin

Basic admin page to view and delete files:

![](admin.png)

---

## Keys

There is a file you can create in `config` called `keys.toml`.

You can copy `keys.toml.example`.

You can add keys to this array to allow users to upload through a bash script.

You'd give a key to each user and they would modify the script to use it.

The example upload script is [here](upload.sh).

The keys file is read every 60 seconds.

So keys can be added or removed without having to restart the server.