from __future__ import annotations

# Standard
from dataclasses import dataclass, asdict
from typing import Any

# Modules
import utils
import database
from config import config
from database import Reaction as DbReaction
from user_procs import User


@dataclass
class Reaction:
    post: str
    user: str
    uname: str
    value: str
    mode: str
    date: int
    ago: str
    uname_str: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def make_reaction(reaction: DbReaction, now: int) -> Reaction:
    ago = utils.time_ago(reaction.date, now)
    uname_str = reaction.uname or "Anon"

    return Reaction(
        reaction.post,
        reaction.user,
        reaction.uname,
        reaction.value,
        reaction.mode,
        reaction.date,
        ago,
        uname_str,
    )


def react(name: str, text: str, user: User, mode: str) -> tuple[str, int]:
    if not user:
        return utils.bad("You are not logged in")

    text = text.strip()

    if not name:
        return utils.bad("Missing values")

    if not text:
        return utils.bad("Missing values")

    if mode not in ["text", "icon"]:
        return utils.bad("Invalid mode")

    if len(text) > max(config.text_reaction_length, 100):
        return utils.bad("Reaction is too long")

    if utils.contains_url(text):
        return utils.bad("No URLs allowed")

    if mode == "text":
        if utils.count_graphemes(text) > config.text_reaction_length:
            return utils.bad("Invalid reaction")
    elif mode == "icon":
        if text not in utils.ICONS:
            return utils.bad("Invalid reaction")

    if database.get_reaction_count(name, user.username) >= config.max_user_reactions:
        return utils.bad("You can't add more reactions")

    dbr = database.add_reaction(name, user.username, user.name, text, mode)

    if dbr:
        reaction = make_reaction(dbr, utils.now())
        database.increase_post_reactions(name)
        database.increase_user_reactions(user.username)
        return utils.ok(data={"reaction": reaction})

    return utils.bad("Reaction failed")
