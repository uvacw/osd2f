import os as _os
import typing as _typing


class Config:
    DEBUG: bool = False
    TESTING: bool = False
    SECRET_KEY: _typing.Optional[str] = None


class Testing(Config):
    TESTING = True


class Development(Config):
    DEBUG = True


class Production(Config):
    DEBUG = False
    TESTING = False
    BIND = "0.0.0.0"
    SECRET_KEY = _os.environ.get("OSD2F_SECRET")


# hypercorn
bind = "0.0.0.0:8000"
