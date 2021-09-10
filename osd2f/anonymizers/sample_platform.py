import typing

from osd2f.logger import logger


async def redact_text(
    entry: typing.Dict[str, typing.Any], _: str = "unused_optional_string"
) -> typing.Dict[str, typing.Any]:
    """Anonymization of posts based on the post title.

    Extract the participants name (e.g. 'user') and correspondent (e.g. "alter")
    from the 'title' field. Then replace occurances of the user and correspondent
    names in the 'data.post' field with `<user>` and `<alter>`.

    """
    if "title" not in entry:
        return entry



    sep_strings = ['commented on',
                    'replied to',
                    ]
    for sep_string in sep_strings:
        if sep_string in entry["title"]:
                ego, rest = entry["title"].split(sep_string)

                alter = rest.split("'")[0]

                entry["title"] = entry["title"].replace(ego, "<user> ").replace(alter, " <alter>")

                if "data" in entry:
                    for data_item in entry["data"]:
                        if comment_author := data_item.get("comment.author"):
                            comment_author = comment_author.replace(ego.strip(), "<user>")
                            comment_author = comment_author.replace(alter.strip(), "<alter>")
                            data_item["comment.author"] = comment_author
                        if comment_comment := data_item.get("comment.comment"):
                            comment_comment = comment_comment.replace(ego.strip(), "<user>")
                            comment_comment = comment_comment.replace(alter.strip(), "<alter>")
                            data_item["comment.comment"] = comment_comment

                return entry


    sep_strings = ['wrote on',
                    'added a new photo to',
                    'was with']

    for sep_string in sep_strings:
        if sep_string in entry["title"]:
            ego, rest = entry["title"].split(sep_string)

            alter = rest.replace("'s timeline.", "")

            entry["title"] = f"<user> {sep_string} <alter>'s timeline."

            if "data" in entry:
                for data_item in entry["data"]:
                    if post := data_item.get("post"):
                        post = post.replace(ego.strip(), "<user>")
                        post = post.replace(alter.strip(), "<alter>")
                        data_item["post"] = post

            return entry

    sep_strings = ['posted in',
                    'shared a',
                    'was travelling to', 
                    'updated his status',
                    'updated her status',
                    'listened to',
                    'added a new',
                    'created a',
                    'checked in',
                    'was at',
                    'is feeling',
                    'was eating',
                    'saved a',
                    'was in',
                    ]

    for sep_string in sep_strings:
        if sep_string in entry["title"]:
            ego, rest = entry["title"].split(sep_string)
            entry["title"] = f"<user> {sep_string} {rest}"

            if "data" in entry:
                for data_item in entry["data"]:
                    if post := data_item.get("post"):
                        post = post.replace(ego.strip(), "<user>")
                        data_item["post"] = post
            return entry

    sep_strings = ['reacted to',
                    'likes',
                    'liked',
                    ]

    for sep_string in sep_strings:
        if sep_string in entry["title"]:
            ego, rest = entry["title"].split(sep_string)

            alter = rest.split("'")[0]

            entry["title"] = entry["title"].replace(ego, "<user> ").replace(alter, " <alter>")

            if "data" in entry:
                for data_item in entry["data"]:
                    if reaction_actor := data_item.get("reaction.actor"):
                        reaction_actor = reaction_actor.replace(ego.strip(), "<user>")
                        reaction_actor = reaction_actor.replace(alter.strip(), "<alter>")
                        data_item["reaction.actor"] = reaction_actor

            return entry

    # Dutch reactions
    sep_strings = ['vindt het bericht',
                    'vindt de foto',
                    'heeft gereageerd op een bericht.',
                    'vindt een bericht leuk.'
                    'vindt de video',
                    'heeft gereageerd op de opmerking',
                    'vond de opmerking',
                    'vindt de link',
                    'vindt een bericht leuk.',
                    'vindt het album',
                    'vindt de video',
                    'vindt de notitie',
                    'vindt een opmerking leuk.',
                    'vindt de opmerking',
                    'vindt een foto leuk.',
                    'vindt de levensgebeurtenis',
                    'vindt zijn eigen opmerking leuk.',
                    'vindt haar eigen opmerking leuk.',
                    'vindt een link leuk.',
                    'vindt de livevideo',
                    'vindt zijn eigen bericht leuk.',
                    'vindt haar eigen bericht leuk.',
                    'heeft gereageerd op een opmerking.',
                    'vindt het leuk dat'




                    ]

    for sep_string in sep_strings:
        if sep_string in entry["title"]:
            ego, rest = entry["title"].split(sep_string)

            alter = rest.split(" van ")
            if len(alter) > 1:
                alter = alter[1]
            else:
                alter = alter[0]
            if ' in ' in alter:
                alter = alter.split(" in ")
                alter = alter[0]
            if len(alter) == 0:
                alter = 'XXXXX'



            entry["title"] = entry["title"].replace(ego, "<user> ").replace(alter, " <alter>")

            if "data" in entry:
                for data_item in entry["data"]:
                    if reaction_actor := data_item.get("reaction.actor"):
                        reaction_actor = reaction_actor.replace(ego.strip(), "<user>")
                        reaction_actor = reaction_actor.replace(alter.strip(), "<alter>")
                        data_item["reaction.actor"] = '<user>'

            return entry

    # Dutch posts
    sep_strings = ['heeft op de tijdlijn',
                    'heeft een link gedeeld',
                    'heeft een bericht geplaatst in',
                    'was  onderweg naar',
                    'was onderweg naar',
                    'heeft zijn status bijgewerkt.',
                    'heeft ingecheckt bij',
                    'heeft iets geschreven op een tijdlijn.',
                    'luisterde naar',
                    'heeft een nieuwe foto toegevoegd aan de tijdlijn',
                    'heeft een afspeellijst gemaakt',
                    'heeft een nieuwe foto toegevoegd.',
                    'was bij',
                    'voelt zich',
                    'was met',
                    'was op weg naar',
                    'was  op weg naar',
                    'heeft een persoon op'


                    
                    ]

    for sep_string in sep_strings:
        if sep_string in entry["title"]:
            ego, rest = entry["title"].split(sep_string)

            alter = rest.split(" van ")
            if len(alter) > 1:
                alter = alter[1]
            else:
                alter = alter[0]
            if ' in ' in alter:
                alter = alter.split(" in ")
                alter = alter[0]
            if len(alter) == 0:
                alter = 'XXXXX'



            entry["title"] = entry["title"].replace(ego.strip(), "<user> ").replace(alter.strip(), " <alter>")

    
            if "data" in entry:
                for data_item in entry["data"]:
                    if post := data_item.get("post"):
                        post = post.replace(ego.strip(), "<user>")
                        post = post.replace(alter.strip(), "<alter>")
                        data_item["post"] = post

            return entry
    

    # Dutch comments
    sep_strings = ['heeft gereageerd op het bericht',
                    'heeft geantwoord op zijn eigen opmerking.',
                    'heeft geantwoord op haar eigen opmerking.',
                    'heeft geantwoord op de opmerking',
                    'heeft gereageerd op een foto',
                    'heeft op de video',
                    'heeft gereageerd op zijn eigen bericht.',
                    'heeft gereageerd op haar eigen bericht.',
                    'heeft een opmerking geplaatst bij een bericht.',
                    'heeft gereageerd op zijn eigen foto.',
                    'heeft gereageerd op haar eigen foto.',
                    'heeft gereageerd op het album',
                    'heeft gereageerd op zijn eigen link.',
                    'heeft gereageerd op haar eigen link.',
                    'heeft gereageerd op de link',
                    'heeft gereageerd op de activiteit',
                    'heeft gereageerd op zijn eigen album.',
                    'heeft een opmerking geplaatst bij de foto',
                    'heeft gereageerd op zijn eigen video.',
                    'heeft gereageerd op haar eigen video.',
                    'heeft een opmerking geplaatst bij het bericht',
                    'heeft gereageerd op de levensgebeurtenis',
                    'heeft geantwoord op een opmerking.',
                    'heeft een opmerking geplaatst bij zijn eigen bericht.',
                    'heeft een opmerking geplaatst bij haar eigen bericht.',
                    'heeft een opmerking geplaatst bij het album',


                    ]


    for sep_string in sep_strings:
        if sep_string in entry["title"]:
            ego, rest = entry["title"].split(sep_string)

            alter = rest.split(" van ")
            if len(alter) > 1:
                alter = alter[1]
            else:
                alter = alter[0]
            if ' in ' in alter:
                alter = alter.split(" in ")
                alter = alter[0]
            if len(alter) == 0:
                alter = 'XXXXX'



            entry["title"] = entry["title"].replace(ego, "<user> ").replace(alter, " <alter>")

    
            if "data" in entry:
                for data_item in entry["data"]:
                    if comment_author := data_item.get("comment.author"):
                        comment_author = comment_author.replace(ego.strip(), "<user>")
                        data_item["comment.author"] = comment_author

            return entry





    else:
        logger.warn("FB post title doesn't match known format.")
        logger.debug(f"post: {entry}")
        return entry




# original
# async def fb_redact_posts_usernames_based_on_title(
#     entry: typing.Dict[str, typing.Any], _: str = "unused_optional_string"
# ) -> typing.Dict[str, typing.Any]:
#     """Anonymization of posts based on the post title.

#     Extract the participants name (e.g. 'user') and correspondent (e.g. "alter")
#     from the 'title' field. Then replace occurances of the user and correspondent
#     names in the 'data.post' field with `<user>` and `<alter>`.

#     """
#     if "title" not in entry:
#         return entry

#     if "wrote on" in entry["title"]:
#         ego, rest = entry["title"].split("wrote on")

#         alter = rest.replace("'s timeline.", "")

#         entry["title"] = "<user> wrote on <alter>'s timeline."

#         if "data" in entry:
#             for data_item in entry["data"]:
#                 if post := data_item.get("post"):
#                     post = post.replace(ego.strip(), "<user>")
#                     post = post.replace(alter.strip(), "<alter>")
#                     data_item["post"] = post

#         return entry

#     if "posted in" in entry["title"]:
#         ego, rest = entry["title"].split("posted in")
#         entry["title"] = f"<user> posted in {rest}"

#         if "data" in entry:
#             for data_item in entry["data"]:
#                 if post := data_item.get("post"):
#                     post = post.replace(ego.strip(), "<user>")
#                     data_item["post"] = post
#         return entry

#     else:
#         logger.warn("FB post title doesn't match known format.")
#         logger.debug(f"post: {entry}")
#         return entry



async def fb_redact_comments(
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
        return entry

    else:
        logger.warn("FB post title doesn't match known format.")
        logger.debug(f"post: {entry}")
        return entry


