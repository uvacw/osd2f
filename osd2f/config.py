import os as _os
import typing as _typing


class Config:
    DEBUG: bool = False
    TESTING: bool = False
    BIND: str = "127.0.0.1"
    PORT: int = 5000
    SECRET_KEY: _typing.Optional[str] = None
    # Allow for BIG submissions 4*16mb for
    # in-memory anonymization.
    # NOTE: protect POST endpoints with
    #       xsrf tokens to avoid memory
    #       based ddos attacks
    MAX_CONTENT_LENGTH: int = 16777216 * 4


class Testing(Config):
    TESTING = True
    DB_URL = "sqlite://:memory:"


class Development(Config):
    DEBUG = True
    DB_URL = _os.environ.get("OSD2F_DB_URL", "sqlite://:memory:")


class Production(Config):
    DEBUG = False
    TESTING = False
    BIND = "0.0.0.0"
    PORT = 8000
    SECRET_KEY = _os.environ.get("OSD2F_SECRET")
    DB_URL = _os.environ.get("OSD2F_DB_URL")


# hypercorn
bind = "0.0.0.0:8000"
