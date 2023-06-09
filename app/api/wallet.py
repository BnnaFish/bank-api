import json
from dataclasses import dataclass
from datetime import datetime

from aiohttp.web import (
    HTTPBadRequest,
    HTTPCreated,
    HTTPNotFound,
    HTTPOk,
    Request,
    StreamResponse,
    json_response,
)
from apischema import ValidationError, deserialize, serialize
from sqlalchemy.exc import IntegrityError

from app.models.wallet import Wallet


@dataclass
class CreateWalletRequest:
    user_id: int


@dataclass
class CreateWalletResponse:
    uuid: str
    created_at: datetime
    amount: int
    user_id: int


async def create_wallet_handler(request: Request) -> StreamResponse:
    try:
        wallet_request = deserialize(CreateWalletRequest, await request.json())
    except ValidationError as err:
        raise HTTPBadRequest(reason=json.dumps(err.errors))
    print(f"New wallet to add: {wallet_request}")

    session = request["session"]
    wallet = Wallet(user_id=wallet_request.user_id)
    session.add(wallet)
    try:
        await session.commit()
    except IntegrityError as err:
        msg = '"wallet" violates foreign key constraint "wallet_user_id_fkey"'
        if msg in str(err.orig):
            print(f"User not exists {repr(err)}")
            raise HTTPBadRequest(reason="User not exists")
        raise
    print(f"New wallet added: {wallet}")
    wallet_dict = serialize(CreateWalletResponse, wallet)
    wallet_json = json.dumps(wallet_dict, default=str)
    return json_response(data=wallet_json, status=HTTPCreated.status_code)


async def get_wallet_handler(request: Request) -> StreamResponse:
    wallet_uuid = request.match_info["wallet_uuid"]
    session = request["session"]
    wallet: Wallet | None = await session.get(Wallet, wallet_uuid)
    if wallet is None:
        raise HTTPNotFound()
    print(f"Return {wallet}")
    wallet_dict = serialize(CreateWalletResponse, wallet)
    wallet_json = json.dumps(wallet_dict, default=str)
    return json_response(data=wallet_json, status=HTTPOk.status_code)
