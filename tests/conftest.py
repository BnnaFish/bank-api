from pytest import fixture

from app.app import init_app


@fixture
async def client(aiohttp_client):
    return await aiohttp_client(init_app())
