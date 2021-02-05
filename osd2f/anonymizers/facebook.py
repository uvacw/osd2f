import typing
from osd2f.logger import logger


async def fb_redact_posts_usernames_based_on_title(
    entry: typing.Dict[str, typing.Any], _: str = "unused_optional_string"
) -> typing.Dict[str, typing.Any]:
    """Anonymization of posts based on the post title.

    Extract the participants name (e.g. 'user') and correspondent (e.g. "alter")
    from the 'title' field. Then replace occurances of the user and correspondent
    names in the 'data.post' field with `<user>` and `<alter>`.

    """
    if "title" not in entry:
        return entry

    if "wrote on" in entry["title"]:
        ego, rest = entry["title"].split("wrote on")

        alter = rest.replace("'s timeline.", "")

        entry["title"] = "<user> wrote on <alter>'s timeline."

        if "data" in entry:
            for data_item in entry["data"]:
                if post := data_item.get("post"):
                    post = post.replace(ego.strip(), "<user>")
                    post = post.replace(alter.strip(), "<alter>")
                    data_item["post"] = post

        return entry

    if "posted in" in entry["title"]:
        ego, rest = entry["title"].split("posted in")
        entry["title"] = f"<user> posted in {rest}"

        if "data" in entry:
            for data_item in entry["data"]:
                if post := data_item.get("post"):
                    post = post.replace(ego.strip(), "<user>")
                    data_item["post"] = post

    else:
        logger.warn("FB post title doesn't match known format.")
        logger.debug(f"post: {entry}")
        return entry
