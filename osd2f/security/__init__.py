"""Security wrappers dynamically set at request time.

Wrapper functions should have the (Callable, *args, **kwargs) -> Response signature.
"""

import os
from functools import wraps

# Wrapper implementations for Authentication
from .authorization.microsoft_msal import microsoft_msal_authentication
from .authorization.not_confgured import no_authentication
from .secrets import azure_keyvault  # Environment secret resolvers
from ..logger import logger  # Global module logger


def authorization_required(func):
    @wraps(func)
    async def decorated_path(*args, **kwargs):
        if os.environ.get("MSAL_CONFIG"):
            logger.info("Using MSAL authentication")
            return await microsoft_msal_authentication(func, *args, **kwargs)
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
    # resolvers
    resolvers = {azure_keyvault.PREFIX: azure_keyvault.azure_keyvault_replace}

    # iterate through environment variables, re-assign if they match a resolver
    # prefix.
    for var, value in os.environ.items():
        for prefix, func in resolvers.items():
            if value.startswith(prefix):
                os.environ[var] = func(value)
