from json import loads

from aiohttp.web import HTTPCreated, HTTPBadRequest


async def test_create_wallet(client):
    resp = await client.post(
        "/api/v1/user",
        json={"name": "foo", "lastname": "bar", "email": "some@gmail.com"},
    )
    user = loads(await resp.json())
    resp = await client.post(
        "/api/v1/wallet",
        json={"user_id": user["id"]},
    )
    assert resp.status == HTTPCreated.status_code
    wallet = loads(await resp.json())
    assert wallet["user_id"] == user["id"]
    assert "uuid" in wallet
    assert wallet["amount"] == 0


async def test_create_wallet_user_not_exists(client):
    resp = await client.post(
        "/api/v1/wallet",
        json={"user_id": 1_000_000},
    )
    assert resp.status == HTTPBadRequest.status_code
    assert resp.reason == "User not exists"
