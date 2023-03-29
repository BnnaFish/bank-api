from json import loads

from aiohttp.web import HTTPBadRequest, HTTPCreated


async def test_create_user(client):
    resp = await client.post(
        "/api/v1/user",
        json={"name": "foo", "lastname": "bar", "email": "some@gmail.com"},
    )
    assert resp.status == HTTPCreated.status_code
    user = loads(await resp.json())
    assert user["name"] == "foo"
    assert user["lastname"] == "bar"
    assert user["email"] == "some@gmail.com"
    assert "id" in user
    assert "created_at" in user


async def test_create_invalid_user(client):
    resp = await client.post(
        "/api/v1/user",
        json={"name": "foo", "lastname": "bar", "email": "bad_email"},
    )
    assert resp.status == HTTPBadRequest.status_code
    assert resp.reason == '[{"loc": [], "err": "Emails should contain \'@\' sign."}]'


async def test_create_duplicated_user(client):
    resp = await client.post(
        "/api/v1/user",
        json={"name": "foo", "lastname": "bar", "email": "other@gmail.com"},
    )
    assert resp.status == HTTPCreated.status_code
    resp = await client.post(
        "/api/v1/user",
        json={"name": "foo", "lastname": "bar", "email": "other@gmail.com"},
    )
    assert resp.status == HTTPBadRequest.status_code
    assert resp.reason == "Email already exists"
