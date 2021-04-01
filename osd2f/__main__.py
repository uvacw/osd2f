#!/usr/bin/env python
import os

from .logger import logger
from .server import start

if mode := os.environ.get("OSD2F_MODE"):
    assert mode in ("Development", "Testing", "Production")
else:
    logger.critical("`OSD2F_MODE` must be set")


if mode and __name__ == "__main__":
    start(mode=mode, run=True)
elif mode:
    app = start(mode=mode, run=False)
