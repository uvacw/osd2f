import asyncio

from tortoise import Tortoise

from .configuration import *  # noqa
from .logs import *  # noqa
from .submissions import *  # noqa


async def initialize_database(db_url: str):
    await Tortoise.init(db_url=db_url, modules={"models": ["osd2f.database"]})
    await Tortoise.generate_schemas(safe=True)
    start_logworker()  # noqa


async def stop_database():
    await asyncio.sleep(0.1)  # to avoid start/stop race-conditions during tests
    await Tortoise.close_connections()
    stop_logworker()  # noqa
