"""Security wrappers dynamically set at request time.

Wrapper functions should have the (Callable, *args, **kwargs) -> Response signature.
"""

import os
from functools import wraps

# Wrapper implementations for Authentication
from .microsoft_msal import microsoft_msal_authentication
from .not_confgured import no_authentication
from ..logger import logger


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
