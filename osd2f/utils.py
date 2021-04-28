import functools
import pathlib
import typing
from collections.abc import MutableMapping

import yaml

from .definitions import Settings
from .logger import logger


@functools.lru_cache
def _cached_load_settings() -> Settings:
    return _load_settings_from_disk()


def _load_settings_from_disk() -> Settings:
    settings_dir = pathlib.Path(__file__).parent.joinpath("settings")
    try:
        settings = Settings.parse_obj(
            yaml.safe_load(open(settings_dir.joinpath("upload_settings.yaml")))
        )
    except FileNotFoundError:
        logger.warning("No user provided `upload_settings.yaml` found, using defaults.")
        settings = Settings.parse_obj(
            yaml.safe_load(open(settings_dir.joinpath("default_upload_settings.yaml")))
        )
    return settings


def load_settings(force_disk: bool = False) -> Settings:
    if force_disk:
        logger.warning(
            "Settings are re-loaded from disk on every request, "
            "this eases debugging, but will hurt performance!"
        )
        return _load_settings_from_disk()
    else:
        return _cached_load_settings()


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
