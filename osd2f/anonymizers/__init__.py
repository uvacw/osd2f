"""Anonymizers

This sub-module contains functions that operate on individual entries
to do some form of anonymization, either by redacting (parts of) strings,
or by omitting entries entirely (e.g. returning None for some entries).

All anonymization functions should have the (entry, optional_string_param)
signature.

Register

"""

import re
import typing

from .facebook import fb_redact_posts_usernames_based_on_title
from ..definitions import Settings, SubmissionList
from ..logger import logger

options: typing.Dict[str, typing.Callable[[typing.Dict, str], typing.Awaitable]] = {
    fb_redact_posts_usernames_based_on_title.__name__: fb_redact_posts_usernames_based_on_title  # noqa
}


async def apply(
    file_entries: typing.List[typing.Dict[str, typing.Any]],
    anonymizer: str,
    optional_str_param: str = "",
) -> typing.List[typing.Dict[str, typing.Any]]:
    if anonymizer not in options:
        logger.warning(
            f"Specified anonymizer {anonymizer} not found. "
            f"Available anonymizers: {options}."
        )
        return []

    anonymized_entries = []
    for entry in file_entries:
        if entry is None:
            continue
        try:
            processed_entry = await options[anonymizer](entry, optional_str_param)
            anonymized_entries.append(processed_entry)
        except:  # noqa
            logger.warning(
                f"anonymizer `{anonymizer}` threw an error while parsing an entry"
            )
            continue

    return anonymized_entries


async def anonymize_submission_list(
    submission_list: SubmissionList, settings: Settings
) -> SubmissionList:
    for i, submission in enumerate(submission_list.__root__):
        logger.debug(f"at submission {i}")
        for filename_pattern, setting in settings.files.items():
            logger.debug(f"matching {filename_pattern} to {submission.filename}")
            if not re.search(filename_pattern, submission.filename):
                continue
            # disregards settings for which no anonymizers are registered
            if not setting.anonymizers:
                continue
            logger.debug(f"Applying {setting.anonymizers} to {submission.filename}")
            # apply all anonymizers registered for file pattern
            for anonymizer in setting.anonymizers:
                function_name, arg = anonymizer.copy().popitem()
                logger.debug(f"Applying {function_name} to {submission.filename}")

                submission_list.__root__[i].entries = await apply(
                    file_entries=submission_list.__root__[i].entries,
                    anonymizer=function_name,
                    optional_str_param=arg,
                )
            # only match the first matching setting
            break
    return submission_list
