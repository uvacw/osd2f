#!/usr/bin/env python
import os

from .logger import logger
from .server import create_app, start_app

if mode := os.environ.get("OSD2F_MODE"):
    assert mode in ("Development", "Testing", "Production")
else:
    logger.critical("`OSD2F_MODE` must be set")


if mode and __name__ == "__main__":
    app = create_app(mode=mode)
    start_app(app)
elif mode:
    app = create_app(mode=mode)
