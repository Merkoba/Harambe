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
    id: int
    post: str
    user: str
    uname: str
    value: str
    mode: str
    date: int
    ago: str
    uname_str: str
    value_sample: str
    date_str: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def make_reaction(reaction: DbReaction, now: int) -> Reaction:
    ago = utils.time_ago(reaction.date, now)
    uname_str = reaction.uname or "Anon"
    value_sample = utils.space_string(reaction.value)[:140]
    date_str = utils.nice_date(reaction.date)

    return Reaction(
        reaction.id,
        reaction.post,
        reaction.user,
        reaction.uname,
        reaction.value,
        reaction.mode,
        reaction.date,
        ago,
        uname_str,
        value_sample,
        date_str,
    )


def react(name: str, text: str, user: User, mode: str) -> tuple[str, int]:
    if not user:
        return utils.bad("You are not logged in")

    if not name:
        return utils.bad("Missing values")

    text = text.strip()
    text = utils.remove_multiple_lines(text)

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


def get_reactionlist() -> list[Reaction]:
    now = utils.now()
    return [make_reaction(reaction, now) for reaction in database.get_reactionlist()]


def get_reactions(
    page: int = 1,
    page_size: str = "default",
    query: str = "",
    sort: str = "date",
    admin: bool = False,
    username: str = "",
    max_reactions: int = 0,
) -> tuple[list[Reaction], str, bool]:
    psize = 0

    if page_size == "default":
        psize = config.admin_page_size
    elif page_size == "all":
        pass  # Don't slice later
    else:
        psize = int(page_size)

    reactions = []
    query = utils.clean_query(query)

    for reaction in get_reactionlist():
        if username:
            if reaction.user != username:
                continue

        ok = (
            not query
            or query in utils.clean_query(reaction.user)
            or query in utils.clean_query(reaction.uname)
            or query in utils.clean_query(reaction.value)
            or query in utils.clean_query(reaction.date_str)
            or query in utils.clean_query(reaction.ago)
            or query in utils.clean_query(reaction.post)
        )

        if not ok:
            continue

        reactions.append(reaction)

    total_str = f"{len(reactions)}"
    sort_reactions(reactions, sort)

    if max_reactions > 0:
        reactions = reactions[:max_reactions]

    if psize > 0:
        start_index = (page - 1) * psize
        end_index = start_index + psize
        has_next_page = end_index < len(reactions)
        reactions = reactions[start_index:end_index]
    else:
        has_next_page = False

    return reactions, total_str, has_next_page


def sort_reactions(reactions: list[Reaction], sort: str) -> None:
    if sort == "date":
        reactions.sort(key=lambda x: x.date, reverse=True)
    elif sort == "date_desc":
        reactions.sort(key=lambda x: x.date, reverse=False)

    if sort == "user":
        reactions.sort(key=lambda x: x.user, reverse=True)
    elif sort == "user_desc":
        reactions.sort(key=lambda x: x.user, reverse=False)

    if sort == "post":
        reactions.sort(key=lambda x: x.post, reverse=True)
    elif sort == "post_desc":
        reactions.sort(key=lambda x: x.post, reverse=False)

    if sort == "value":
        reactions.sort(key=lambda x: x.value, reverse=True)
    elif sort == "value_desc":
        reactions.sort(key=lambda x: x.value, reverse=False)

    if sort == "date":
        reactions.sort(key=lambda x: x.date, reverse=True)
    elif sort == "date_desc":
        reactions.sort(key=lambda x: x.date, reverse=False)


def delete_reactions(ids: list[int]) -> tuple[str, int]:
    if not ids:
        return utils.bad("Ids were not provided")

    for id_ in ids:
        do_delete_reaction(id_)

    return utils.ok("Reaction deleted successfully")


def delete_reaction(id_: int, user: User) -> tuple[str, int]:
    if not id_:
        return utils.bad("Id was not provided")

    if not user:
        return utils.bad("You are not logged in")

    reaction = database.get_reaction(id_)

    if not reaction:
        return utils.bad("Reaction not found")

    if reaction.user != user.username:
        if not user.admin:
            return utils.bad("You can't delete this reaction")

    do_delete_reaction(id_)
    return utils.ok("Reaction deleted successfully")


def do_delete_reaction(id_: int) -> None:
    if not id_:
        return

    database.delete_reaction(id_)


def delete_all_reactions() -> tuple[str, int]:
    database.delete_all_reactions()
    return utils.ok("All reactions deleted")
