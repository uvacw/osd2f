from tortoise import Tortoise

from .configuration import *
from .logs import *
from .submissions import *


async def initialize_database(db_url: str):
    await Tortoise.init(db_url=db_url, modules={"models": ["osd2f.database"]})
    await Tortoise.generate_schemas(safe=True)
    start_logworker()


async def stop_database():
    await Tortoise.close_connections()
    stop_logworker()