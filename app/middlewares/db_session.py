from typing import Awaitable, Callable

from aiohttp.web import Request, StreamResponse, middleware
from sqlalchemy.ext.asyncio import async_sessionmaker

THandler = Callable[..., Awaitable[StreamResponse]]


@middleware
async def sa_session_middleware(
    request: Request,
    handler: THandler,  # noqa: WPS110 Found wrong variable name: handler,
) -> StreamResponse:
    engine = request.app["db"]
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        request["session"] = session
        return await handler(request)
