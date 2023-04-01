from aiohttp import web

from app.api.transaction import (
    create_transaction_handler,
    get_transaction_handler,
    get_transactions_handler,
)
from app.api.user import create_user_handler
from app.api.wallet import create_wallet_handler, get_wallet_handler
from app.cleanups.database import close_db
from app.middlewares.db_session import sa_session_middleware
from app.startups.config import init_config
from app.startups.database import init_db


def init_app() -> web.Application:
    app = web.Application(middlewares=[sa_session_middleware])

    # Startups
    app.on_startup.append(init_config)
    app.on_startup.append(init_db)

    # Cleanups
    app.on_cleanup.append(close_db)

    app.add_routes(
        [
            web.post("/api/v1/users", create_user_handler),
            web.post("/api/v1/wallets", create_wallet_handler),
            web.get("/api/v1/wallet/{wallet_uuid}", get_wallet_handler),
            web.post("/api/v1/transactions", create_transaction_handler),
            web.get("/api/v1/transaction/{transaction_uuid}", get_transaction_handler),
            web.get("/api/v1/transactions", get_transactions_handler),
        ],
    )
    return app
