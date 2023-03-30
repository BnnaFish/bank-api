import json
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from aiohttp.web import (
    HTTPBadRequest,
    HTTPCreated,
    HTTPNotFound,
    HTTPOk,
    HTTPPaymentRequired,
    Request,
    StreamResponse,
    json_response,
)
from apischema import ValidationError, deserialize, serialize, validator
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction, TransactionType
from app.models.wallet import Wallet


@dataclass
class CreateTransactionRequest:
    wallet_uuid: UUID
    amount: int
    type: TransactionType

    @validator
    def positive_amount(self):
        if self.amount <= 0:
            yield f"Amount should be positive, but got {self.amount}"


@dataclass
class TransactionResponse(CreateTransactionRequest):
    uuid: UUID
    balance_before: int
    balance_after: int


@dataclass
class GetTransactionsRequest:
    wallet_uuid: UUID
    to_date: int


async def create_transaction_handler(request: Request) -> StreamResponse:
    try:
        transaction_request = deserialize(
            CreateTransactionRequest,
            await request.json(),
        )
    except ValidationError as err:
        raise HTTPBadRequest(reason=json.dumps(err.errors))
    print(f"New transaction to add: {transaction_request}")

    session: AsyncSession = request["session"]
    wallet: Wallet | None = await session.get(
        Wallet,
        transaction_request.wallet_uuid,
        with_for_update=True,
    )
    if wallet is None:
        raise HTTPNotFound()
    balance_before = wallet.amount
    match transaction_request.type:
        case TransactionType.DEPOSIT:
            wallet.amount += transaction_request.amount
        case TransactionType.WITHDRAW:
            if wallet.amount - transaction_request.amount < 0:
                raise HTTPPaymentRequired(
                    reason=(
                        f"Not sufficient funds. Got: {wallet.amount},"
                        f"required: {transaction_request.amount}"
                    ),
                )
            wallet.amount -= transaction_request.amount
    transaction = Transaction(
        type=transaction_request.type,
        amount=transaction_request.amount,
        balance_before=balance_before,
        balance_after=wallet.amount,
        wallet_uuid=wallet.uuid,
    )
    session.add(wallet)
    session.add(transaction)
    await session.commit()
    print(f"New transaction added: {transaction}")
    transaction_dict = serialize(TransactionResponse, transaction)
    transaction_json = json.dumps(transaction_dict, default=str)
    return json_response(data=transaction_json, status=HTTPCreated.status_code)


async def get_transaction_handler(request: Request) -> StreamResponse:
    transaction_uuid = request.match_info["transaction_uuid"]
    session = request["session"]
    transaction: Transaction | None = await session.get(Transaction, transaction_uuid)
    if transaction is None:
        return HTTPNotFound()
    print(f"Return {transaction}")
    transaction_dict = serialize(TransactionResponse, transaction)
    transaction_json = json.dumps(transaction_dict, default=str)
    return json_response(data=transaction_json, status=HTTPOk.status_code)


async def get_transactions_handler(request: Request) -> StreamResponse:
    try:
        get_transactions_request = deserialize(
            GetTransactionsRequest,
            await request.json(),
        )
    except ValidationError as err:
        raise HTTPBadRequest(reason=json.dumps(err.errors))
    print(f"Get transactions request: {get_transactions_request}")
    max_date = datetime.fromtimestamp(get_transactions_request.to_date)

    session = request["session"]
    statement = (
        select(Transaction)
        .where(Transaction.wallet_uuid == get_transactions_request.wallet_uuid)
        .filter(Transaction.created_at <= max_date)
        .order_by(desc(Transaction.created_at))
    )
    last_transaction = (await session.execute(statement)).scalars().first()
    if last_transaction is None:
        return HTTPNotFound()
    print(f"Found transaction: {last_transaction}")
    transaction_dict = serialize(TransactionResponse, last_transaction)
    transaction_json = json.dumps(transaction_dict, default=str)
    return json_response(data=transaction_json, status=HTTPOk.status_code)
