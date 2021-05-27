import datetime
import functools
import os
import pathlib
import pytz
import typing
from collections.abc import MutableMapping

import yaml

from .database import set_content_config, get_content_config
from .definitions import ContentSettings, UploadSettings
from .logger import logger

# TODO Restructure:
# - accept settings from CLI args
# - generically apply cashing of CLI location

DISK_CONFIG_VERSION = ""


@functools.lru_cache
def _cached_load_settings() -> UploadSettings:
    return _load_settings_from_disk()


def _load_settings_from_disk() -> UploadSettings:
    settings_dir = pathlib.Path(__file__).parent.joinpath("settings")
    try:
        settings = UploadSettings.parse_obj(
            yaml.safe_load(open(settings_dir.joinpath("upload_settings.yaml")))
        )
    except FileNotFoundError:
        logger.warning("No user provided `upload_settings.yaml` found, using defaults.")
        settings = UploadSettings.parse_obj(
            yaml.safe_load(open(settings_dir.joinpath("default_upload_settings.yaml")))
        )
    return settings


def load_upload_settings(force_disk: bool = False) -> UploadSettings:
    if force_disk:
        logger.warning(
            "Settings are re-loaded from disk on every request, "
            "this eases debugging, but will hurt performance!"
        )
        return _load_settings_from_disk()
    else:
        return _cached_load_settings()


async def load_content_settings(use_cache: bool) -> ContentSettings:
    settings_dir = pathlib.Path(__file__).parent.joinpath("settings")

    # load db config version
    db_config = await get_content_config()

    # load disk version ()
    disk_config = (
        yaml.safe_load(open(settings_dir.joinpath("default_content_settings.yaml")))
        if (not DISK_CONFIG_VERSION and not use_cache)
        else DISK_CONFIG_VERSION
    )

    disk_timestamp = pytz.UTC.localize(
        datetime.datetime.fromtimestamp(
            os.path.getmtime(settings_dir.joinpath("default_content_settings.yaml"))
        )
    )

    # if no database config exists, insert disk version in database and
    # use disk version
    if not db_config:
        config = ContentSettings.parse_obj(disk_config)
        await set_content_config(user="default", content=config)
        return config

    # pick the most recent version
    if db_config.insert_timestamp > disk_timestamp:
        last_config = db_config.config_blob
    else:
        last_config = disk_config

    config = ContentSettings.parse_obj(last_config)

    return config


def flatten(d: MutableMapping, parent_key: str = "", sep: str = "_"):
    items = []
    if type(d) == str:
        return d
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        elif type(v) == list:
            items.append((new_key, [flatten(vi, sep=sep) for vi in v]))
        else:
            items.append((new_key, v))
    return dict(items)


def flatmap(
    items: dict,
    in_key: typing.Optional[str] = None,
):

    base = items if in_key is None else items.get(in_key, [])

    return [flatten(e, sep=".") for e in base]
