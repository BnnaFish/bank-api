from aiohttp import web

from app.settings import database_config


async def init_config(app: web.Application) -> None:
    app["database_config"] = database_config
