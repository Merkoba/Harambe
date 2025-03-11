from __future__ import annotations

# Standard
from dataclasses import dataclass, asdict
from typing import Any

# Modules
import utils
import database
import post_procs
from config import config
from database import Reaction as DbReaction
from user_procs import User


@dataclass
class Reaction:
    id: int
    post_id: int
    user_id: int
    pname: str
    username: str
    uname: str
    value: str
    listed: bool
    date: int
    ago: str
    value_sample: str
    date_str: str
    pshow: str
    pmtype: str
    ptitle: str
    pfull: str
    poriginal: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def make_reaction(reaction: DbReaction, now: int) -> Reaction:
    ago = utils.time_ago(reaction.date, now)
    value_sample = utils.space_string(reaction.value)[:140]
    date_str = utils.nice_date(reaction.date)

    if reaction.parent:
        pname = reaction.parent.name
        pshow = f"{reaction.parent.name} {reaction.parent.ext}".strip()
        pmtype = reaction.parent.mtype
        ptitle = reaction.parent.title
        poriginal = reaction.parent.original
        pfull = post_procs.get_full_name(reaction.parent)
    else:
        pname = "?"
        pshow = "?"
        pmtype = "?"
        ptitle = "?"
        pfull = "?"
        poriginal = "?"

    if reaction.author:
        username = reaction.author.username
        uname = reaction.author.name or "Anon"
        listed = reaction.author.lister
    else:
        username = "?"
        uname = "Anon"
        listed = False

    return Reaction(
        reaction.id,
        reaction.post,
        reaction.user,
        pname,
        username,
        uname,
        reaction.value,
        listed,
        reaction.date,
        ago,
        value_sample,
        date_str,
        pshow,
        pmtype,
        ptitle,
        pfull,
        poriginal,
    )


def add_reaction(post_id: int, text: str, user: User) -> tuple[str, int]:
    if not user:
        return utils.bad("You are not logged in")

    if not post_id:
        return utils.bad("Missing values")

    text = text.strip()
    text = utils.remove_multiple_lines(text)

    if not text:
        return utils.bad("Missing values")

    if not check_reaction(text):
        return utils.bad("Invalid reaction")

    if database.get_reaction_count(post_id, user.id) >= config.max_user_reactions:
        return utils.bad("You can't add more reactions")

    reaction_id = database.add_reaction(post_id, user.id, text)

    if not reaction_id:
        return utils.bad("Reaction failed")

    reaction = get_reaction(reaction_id)

    if reaction:
        return utils.ok(data={"reaction": reaction})

    return utils.bad("Reaction failed")


def get_reaction(reaction_id: int) -> Reaction | None:
    if not reaction_id:
        return None

    reactions = database.get_reactions(reaction_id)
    reaction = reactions[0] if reactions else None

    if not reaction:
        return None

    return make_reaction(reaction, utils.now())


def get_reactionlist(user_id: int | None = None) -> list[Reaction]:
    now = utils.now()
    reactions = database.get_reactions(user_id=user_id)
    return [make_reaction(reaction, now) for reaction in reactions]


def get_reactions(
    page: int = 1,
    page_size: str = "default",
    query: str = "",
    sort: str = "date",
    admin: bool = False,
    user_id: int | None = None,
    max_reactions: int = 0,
    only_listed: bool = False,
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

    for reaction in get_reactionlist(user_id):
        if only_listed:
            if not reaction.listed:
                continue

        ok = (
            not query
            or (admin and (query in utils.clean_query(reaction.username)))
            or query in utils.clean_query(reaction.pname)
            or query in utils.clean_query(reaction.uname)
            or query in utils.clean_query(reaction.value)
            or query in utils.clean_query(reaction.date_str)
            or query in utils.clean_query(reaction.ago)
            or query in utils.clean_query(reaction.pshow)
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
        reactions.sort(key=lambda x: x.uname, reverse=True)
    elif sort == "user_desc":
        reactions.sort(key=lambda x: x.uname, reverse=False)

    if sort == "post":
        reactions.sort(key=lambda x: x.pname, reverse=True)
    elif sort == "post_desc":
        reactions.sort(key=lambda x: x.pname, reverse=False)

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

    for reaction_id in ids:
        do_delete_reaction(reaction_id)

    return utils.ok("Reaction deleted successfully")


def delete_reaction(reaction_id: int, user: User) -> tuple[str, int]:
    if not reaction_id:
        return utils.bad("Id was not provided")

    if not user:
        return utils.bad("You are not logged in")

    reaction = get_reaction(reaction_id)

    if not reaction:
        return utils.bad("Reaction not found")

    if not user.admin:
        if not config.allow_edit:
            return utils.bad("Editing is disabled")

        if reaction.user_id != user.id:
            if not user.admin:
                return utils.bad("You can't delete this reaction")

    do_delete_reaction(reaction_id)
    return utils.ok("Reaction deleted successfully")


def do_delete_reaction(reaction_id: int) -> None:
    if not reaction_id:
        return

    database.delete_reaction(reaction_id)


def delete_all_reactions() -> tuple[str, int]:
    database.delete_all_reactions()
    return utils.ok("All reactions deleted")


def edit_reaction(reaction_id: int, text: str, user: User) -> tuple[str, int]:
    if not reaction_id:
        return utils.bad("Id was not provided")

    if not user:
        return utils.bad("You are not logged in")

    if not text:
        return utils.bad("Missing values")

    text = text.strip()
    text = utils.remove_multiple_lines(text)

    if not text:
        return utils.bad("Missing values")

    if not check_reaction(text):
        return utils.bad("Invalid reaction")

    reaction = get_reaction(reaction_id)

    if not reaction:
        return utils.bad("Reaction not found")

    if not user.admin:
        if not config.allow_edit:
            return utils.bad("Editing is disabled")

        if reaction.user_id != user.id:
            return utils.bad("You can't edit this reaction")

    database.edit_reaction(reaction_id, text)
    new_reaction = get_reaction(reaction_id)

    if new_reaction:
        return utils.ok(data={"reaction": new_reaction})

    return utils.bad("Reaction edit failed")


def check_reaction(text: str) -> bool:
    if len(text) > max(config.text_reaction_length, 100):
        return False

    if utils.contains_url(text):
        return False

    return utils.count_graphemes(text) <= config.text_reaction_length
