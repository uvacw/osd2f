"""Anonymizers

This sub-module contains functions that operate on individual entries
to do some form of anonymization, either by redacting (parts of) strings,
or by omitting entries entirely (e.g. returning None for some entries).

All anonymization functions should have the (entry, optional_string_param)
signature.

Register

"""

import typing

from ..logger import logger
from .facebook import fb_redact_posts_usernames_based_on_title

options: typing.Dict[
    str,
    typing.Callable[
        [typing.Dict[typing.AnyStr, typing.Any], typing.Optional[str]],
        typing.Dict[str, typing.Any],
    ],
] = {
    fb_redact_posts_usernames_based_on_title.__name__: fb_redact_posts_usernames_based_on_title
}


async def apply(
    file_entries: typing.Iterable[typing.Dict],
    anonymizer: str,
    optional_str_param: str = "",
) -> typing.List[typing.Dict[str, typing.Any]]:
    if anonymizer not in options:
        logger.warning(
            f"Specified anonymizer {anonymizer} not found. Available anonymizers: {options}."
        )
        return []
    anonymized_entries = [
        options[anonymizer](entry, optional_str_param)
        for entry in file_entries
        if entry is not None
    ]
    return anonymized_entries
