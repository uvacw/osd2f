import functools
import pathlib
from typing import Dict

import yaml

from .logger import logger


@functools.cache
def load_settings() -> Dict:
    settings_dir = pathlib.Path(__file__).parent.parent.joinpath("settings")
    try:
        settings = yaml.load(open(settings_dir.joinpath("upload_settings.yaml")))
    except FileNotFoundError:
        logger.warning("No user provided `upload_settings.yaml` found, using defaults.")
        settings = yaml.load(
            open(settings_dir.joinpath("default_upload_settings.yaml"))
        )
    return settings
