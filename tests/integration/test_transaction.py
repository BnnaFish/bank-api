import asyncio
from datetime import datetime, timedelta
from json import loads

from aiohttp.web import HTTPCreated, HTTPNotFound, HTTPOk, HTTPPaymentRequired
from freezegun import freeze_time


async def test_create_transaction_deposit(client):
    # add new user
    resp = await client.post(
        "/api/v1/users",
        json={"name": "foo", "lastname": "bar", "email": "some@gmail.com"},
    )
    user = loads(await resp.json())
    # add new wallet
    resp = await client.post(
        "/api/v1/wallets",
        json={"user_id": user["id"]},
    )
    wallet = loads(await resp.json())
    wallet_uuid = wallet["uuid"]

    # make new transaction
    resp = await client.post(
        "/api/v1/transactions",
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
        "/api/v1/users",
        json={"name": "foo", "lastname": "bar", "email": "some@gmail.com"},
    )
    user = loads(await resp.json())
    # add new wallet
    resp = await client.post(
        "/api/v1/wallets",
        json={"user_id": user["id"]},
    )
    wallet = loads(await resp.json())
    wallet_uuid = wallet["uuid"]

    # deposit some money
    resp = await client.post(
        "/api/v1/transactions",
        json={"wallet_uuid": wallet_uuid, "amount": 100, "type": "DEPOSIT"},
    )
    assert resp.status == HTTPCreated.status_code

    # withdraw money
    resp = await client.post(
        "/api/v1/transactions",
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
        "/api/v1/users",
        json={"name": "foo", "lastname": "bar", "email": "some@gmail.com"},
    )
    user = loads(await resp.json())
    # add new wallet
    resp = await client.post(
        "/api/v1/wallets",
        json={"user_id": user["id"]},
    )
    wallet = loads(await resp.json())
    wallet_uuid = wallet["uuid"]

    # deposit some money
    resp = await client.post(
        "/api/v1/transactions",
        json={"wallet_uuid": wallet_uuid, "amount": 100, "type": "DEPOSIT"},
    )
    assert resp.status == HTTPCreated.status_code

    # withdraw money
    resp = await client.post(
        "/api/v1/transactions",
        json={"wallet_uuid": wallet_uuid, "amount": 200, "type": "WITHDRAW"},
    )
    assert resp.status == HTTPPaymentRequired.status_code

    # wallet should be without withdraw
    resp = await client.get(f"/api/v1/wallet/{wallet_uuid}")
    assert resp.status == HTTPOk.status_code
    wallet_get = loads(await resp.json())
    assert wallet_get["amount"] == 100


async def test_transactions(client):
    # add new user
    resp = await client.post(
        "/api/v1/users",
        json={"name": "foo", "lastname": "bar", "email": "some@gmail.com"},
    )
    user = loads(await resp.json())
    # add new wallet
    resp = await client.post(
        "/api/v1/wallets",
        json={"user_id": user["id"]},
    )
    wallet = loads(await resp.json())
    wallet_uuid = wallet["uuid"]

    first_trs_date = datetime(year=2000, month=1, day=1)
    between_date = first_trs_date + timedelta(days=15)
    between_timestamp = int(between_date.timestamp())
    second_trs_date = between_date + timedelta(days=30)
    after_second_trs_date = second_trs_date + timedelta(days=30)
    after_second_trs_timestamp = int(after_second_trs_date.timestamp())

    # deposit some money
    with freeze_time(first_trs_date):
        resp = await client.post(
            "/api/v1/transactions",
            json={"wallet_uuid": wallet_uuid, "amount": 100, "type": "DEPOSIT"},
        )
        assert resp.status == HTTPCreated.status_code

    # deposit some money month after
    with freeze_time(second_trs_date):
        resp = await client.post(
            "/api/v1/transactions",
            json={"wallet_uuid": wallet_uuid, "amount": 100, "type": "DEPOSIT"},
        )
        assert resp.status == HTTPCreated.status_code

    # get before first transaction
    resp = await client.get(
        f"/api/v1/transactions", json={"wallet_uuid": wallet_uuid, "to_date": 1}
    )
    assert resp.status == HTTPNotFound.status_code

    # get after first trs
    resp = await client.get(
        f"/api/v1/transactions",
        json={"wallet_uuid": wallet_uuid, "to_date": between_timestamp},
    )
    assert resp.status == HTTPOk.status_code
    transaction = loads(await resp.json())
    assert transaction["balance_after"] == 100

    # get after second trs
    resp = await client.get(
        f"/api/v1/transactions",
        json={"wallet_uuid": wallet_uuid, "to_date": after_second_trs_timestamp},
    )
    assert resp.status == HTTPOk.status_code
    transaction = loads(await resp.json())
    assert transaction["balance_after"] == 200
