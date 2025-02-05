from __future__ import annotations

# Standard
from typing import Any

# Libraries
from flask import Flask, render_template, request, Response  # type: ignore
from flask_cors import CORS  # type: ignore
from flask_simple_captcha import CAPTCHA  # type: ignore
from flask_limiter import Limiter  # type: ignore
from flask_limiter.util import get_remote_address  # type: ignore
from flask import send_from_directory  # type: ignore

# Modules
import config as Config
import procs as Procs


# ---


app = Flask(__name__)

# Enable all cross origin requests
CORS(app)

simple_captcha = CAPTCHA(config=Config.captcha)
app = simple_captcha.init_app(app)
rate_limit = f"{Config.rate_limit} per minute"
rate_limit_change = f"{Config.rate_limit_change} per minute"

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[rate_limit],
    storage_uri="redis://localhost:6379",
    strategy="fixed-window",
)


# ---


invalid = "Error: Invalid request"


@app.route("/", methods=["POST", "GET"])  # type: ignore
@limiter.limit(rate_limit)  # type: ignore
def index() -> Any:
    if request.method == "POST":
        try:
            message = Procs.upload(request)
            return render_template("message.html", message=message)
        except Exception as e:
            print(e)
            return Response(invalid, mimetype=Config.text_mtype)

    captcha = simple_captcha.create()
    return render_template("index.html", captcha=captcha)


@app.route("/files/<path:filename>", methods=["GET"])  # type: ignore
@limiter.limit(rate_limit)  # type: ignore
def get_file(filename: str) -> Any:
    return send_from_directory("files", filename)
