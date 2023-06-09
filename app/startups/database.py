from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine

from app.models.base import Base
from app.settings import DatabaseConfig


async def init_db(app: web.Application):
    database_config: DatabaseConfig = app["database_config"]
    engine = create_async_engine(
        "postgresql+asyncpg://"
        f"{database_config.user}:{database_config.password}"
        "@"
        f"{database_config.host}:{database_config.port}/{database_config.schema}",
    )
    app["db"] = engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
