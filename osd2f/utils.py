import functools
import pathlib

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
