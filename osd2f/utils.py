import functools
import pathlib
from typing import Dict
import typing

import yaml

from .logger import logger


@functools.cache
def _cached_load_settings() -> Dict:
    return _load_settings_from_disk()


def _load_settings_from_disk() -> Dict:
    settings_dir = pathlib.Path(__file__).parent.parent.joinpath("settings")
    try:
        settings = yaml.load(open(settings_dir.joinpath("upload_settings.yaml")))
    except FileNotFoundError:
        logger.warning("No user provided `upload_settings.yaml` found, using defaults.")
        settings = yaml.load(
            open(settings_dir.joinpath("default_upload_settings.yaml"))
        )
    return settings


def load_settings(force_disk: bool = False):
    if force_disk:
        logger.warning(
            "Settings are re-loaded from disk on every request, "
            "this eases debugging, but will hurt performance!"
        )
        return _load_settings_from_disk()
    else:
        return _cached_load_settings()


def validate_data(
    data: typing.Dict[str, typing.List[typing.Dict]]
) -> typing.Dict[str, typing.List[typing.Dict]]:
    return data