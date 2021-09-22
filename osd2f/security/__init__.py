"""Security wrappers dynamically set at request time.

Wrapper functions should have the (Callable, *args, **kwargs) -> Response signature.
"""

import os
from functools import wraps

# Wrapper implementations for Authentication
from .authorization.basic_auth import basic_authentication
from .authorization.microsoft_msal import microsoft_msal_authentication
from .authorization.not_confgured import no_authentication
from .download_encryption.encrypted_zipfile import string_to_zipfile  # noqa
from .secrets import azure_keyvault  # Environment secret resolvers
from ..logger import logger  # Global module logger

RESOLVERS = {azure_keyvault.PREFIX: azure_keyvault.azure_keyvault_replace}


def authorization_required(func):
    """A decorator that implements authorization depending on configuration"""

    @wraps(func)
    async def decorated_path(*args, **kwargs):
        if os.environ.get("MSAL_CONFIG"):
            logger.info("Using MSAL authentication")
            return await microsoft_msal_authentication(func, *args, **kwargs)
        if os.environ.get("OSD2F_BASIC_AUTH"):
            logger.info("Using basic auth, NOT RECOMMENDED FOR PRODUCTION")
            return await basic_authentication(func, *args, **kwargs)
        else:
            logger.info("Fall back to no authentication")
            return await no_authentication(func, *args, **kwargs)

    return decorated_path


def translate_environment_vars():
    """Translate environment variable values to their secrets.

    Assumes environment variables matching a pattern:
     `SECRETSTORE_PREFIX::DELIMITED::ARGUMENTS`

    should be translated by their respective resolver functions.

    """
    # iterate through environment variables, re-assign if they match a resolver
    # prefix.
    for var, value in os.environ.items():
        for prefix, func in RESOLVERS.items():
            if value.startswith(prefix):
                os.environ[var] = func(value)


def translate_value(value: str) -> str:
    """Translate a given value to the appropriate secret.

    Assumes the value matches a pattern of a known resolver, e.g.:
        `SECRETSTORE_PREFIX::DELIMITED::ARGUMENTS`

    secrets are resolved by their matching RESOLVERS function.

    String not matching any known prefix are ignored.
    """
    for prefix, func in RESOLVERS.items():
        if value.startswith(prefix):
            logger.debug(f"{value} resolved using {func.__name__}")
            return func(value)

    logger.debug(f"{value} did not match any registered resolver.")
    return value
