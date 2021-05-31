"""Contains the route-override when no authentication is configured
"""


async def no_authentication(func, *args, **kwargs):
    return (
        "Page unavailable: Authorization must be configured "
        "unless the app is in testing or debug mode.",
        501,
    )
