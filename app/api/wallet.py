from dataclasses import dataclass
from datetime import datetime
from json import dumps

from aiohttp.web import (
    Request,
    StreamResponse,
    HTTPBadRequest,
    HTTPCreated,
    json_response,
)
from apischema import ValidationError, deserialize, serialize
from sqlalchemy.exc import IntegrityError


from app.models.user import User
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
        raise HTTPBadRequest(reason=dumps(err.errors))
    print(f"New wallet to add: {wallet_request}")

    session = request["session"]
    wallet = Wallet(user_id=wallet_request.user_id)
    session.add(wallet)
    try:
        await session.commit()
    except IntegrityError as err:
        if (
            'insert or update on table "wallet" violates foreign key constraint "wallet_user_id_fkey"'
            in str(err.orig)
        ):
            print(f"User not exists {repr(err)}")
            raise HTTPBadRequest(reason="User not exists")
        raise
    print(f"New wallet added: {wallet}")
    user_dict = serialize(CreateWalletResponse, wallet)
    user_json = dumps(user_dict, default=str)
    return json_response(data=user_json, status=HTTPCreated.status_code)
