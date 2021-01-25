import typing


async def fb_redact_posts_usernames_based_on_title(
    entry: typing.Dict[str, typing.Dict], _: str = "unused_optional_string"
) -> typing.Dict[str, typing.Any]:
    """Anonymization of posts based on the post title.

    Extract the participants name (e.g. 'user') and correspondent (e.g. "alter")
    from the 'title' field. Then replace occurances of the user and correspondent
    names in the 'data.post' field with `<user>` and `<alter>`.

    """
    if "title" not in entry:
        return entry
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