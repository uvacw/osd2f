import os as _os
import typing as _typing


class Config:
    DEBUG: bool = False
    TESTING: bool = False
    SECRET_KEY: _typing.Optional[str] = None


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
    SECRET_KEY = _os.environ.get("OSD2F_SECRET")
    DB_URL = _os.environ.get("OSD2F_DB_URL")


# hypercorn
bind = "0.0.0.0:8000"
