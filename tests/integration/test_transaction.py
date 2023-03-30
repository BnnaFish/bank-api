import asyncio
from json import loads
from pydoc import cli

from aiohttp.web import HTTPCreated, HTTPOk, HTTPPaymentRequired


async def test_create_transaction_deposit(client):
    # add new user
    resp = await client.post(
        "/api/v1/user",
        json={"name": "foo", "lastname": "bar", "email": "some@gmail.com"},
    )
    user = loads(await resp.json())
    # add new wallet
    resp = await client.post(
        "/api/v1/wallet",
        json={"user_id": user["id"]},
    )
    wallet = loads(await resp.json())
    wallet_uuid = wallet["uuid"]

    # make new transaction
    resp = await client.post(
        "/api/v1/transaction",
        json={"wallet_uuid": wallet_uuid, "amount": 100, "type": "DEPOSIT"},
    )
    assert resp.status == HTTPCreated.status_code
    transaction = loads(await resp.json())
    assert transaction["wallet_uuid"] == wallet_uuid
    assert "uuid" in wallet
    assert transaction["amount"] == 100
    assert transaction["balance_before"] == 0
    assert transaction["balance_after"] == 100

    # get transaction should return the same
    resp = await client.get(f"/api/v1/transaction/{transaction['uuid']}")
    assert resp.status == HTTPOk.status_code
    transaction_get = loads(await resp.json())
    assert transaction_get["wallet_uuid"] == wallet_uuid
    assert "uuid" in wallet
    assert transaction_get["amount"] == 100
    assert transaction_get["balance_before"] == 0
    assert transaction_get["balance_after"] == 100

    # and wallet updated as well
    resp = await client.get(f"/api/v1/wallet/{wallet_uuid}")
    assert resp.status == HTTPOk.status_code
    wallet_get = loads(await resp.json())
    assert wallet_get["amount"] == 100


async def test_transaction_withdraw(client):
    # add new user
    resp = await client.post(
        "/api/v1/user",
        json={"name": "foo", "lastname": "bar", "email": "some@gmail.com"},
    )
    user = loads(await resp.json())
    # add new wallet
    resp = await client.post(
        "/api/v1/wallet",
        json={"user_id": user["id"]},
    )
    wallet = loads(await resp.json())
    wallet_uuid = wallet["uuid"]

    # deposit some money
    resp = await client.post(
        "/api/v1/transaction",
        json={"wallet_uuid": wallet_uuid, "amount": 100, "type": "DEPOSIT"},
    )
    assert resp.status == HTTPCreated.status_code

    # withdraw money
    resp = await client.post(
        "/api/v1/transaction",
        json={"wallet_uuid": wallet_uuid, "amount": 99, "type": "WITHDRAW"},
    )
    transaction = loads(await resp.json())
    assert transaction["wallet_uuid"] == wallet_uuid
    assert "uuid" in wallet
    assert transaction["amount"] == 99
    assert transaction["balance_before"] == 100
    assert transaction["balance_after"] == 1

    # get transaction should return the same
    resp = await client.get(f"/api/v1/transaction/{transaction['uuid']}")
    assert resp.status == HTTPOk.status_code
    transaction_get = loads(await resp.json())
    assert transaction_get["wallet_uuid"] == wallet_uuid
    assert "uuid" in wallet
    assert transaction_get["amount"] == 99
    assert transaction_get["balance_before"] == 100
    assert transaction_get["balance_after"] == 1


async def test_transaction_no_money_no_honey(client):
    # add new user
    resp = await client.post(
        "/api/v1/user",
        json={"name": "foo", "lastname": "bar", "email": "some@gmail.com"},
    )
    user = loads(await resp.json())
    # add new wallet
    resp = await client.post(
        "/api/v1/wallet",
        json={"user_id": user["id"]},
    )
    wallet = loads(await resp.json())
    wallet_uuid = wallet["uuid"]

    # deposit some money
    resp = await client.post(
        "/api/v1/transaction",
        json={"wallet_uuid": wallet_uuid, "amount": 100, "type": "DEPOSIT"},
    )
    assert resp.status == HTTPCreated.status_code

    # withdraw money
    resp = await client.post(
        "/api/v1/transaction",
        json={"wallet_uuid": wallet_uuid, "amount": 200, "type": "WITHDRAW"},
    )
    assert resp.status == HTTPPaymentRequired.status_code

    # wallet should be without withdraw
    resp = await client.get(f"/api/v1/wallet/{wallet_uuid}")
    assert resp.status == HTTPOk.status_code
    wallet_get = loads(await resp.json())
    assert wallet_get["amount"] == 100
