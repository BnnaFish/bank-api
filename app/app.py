from aiohttp import web

from app.api.user import create_user_handler
from app.api.wallet import create_wallet_handler
from app.cleanups.database import close_db
from app.middlewares.db_session import sa_session_middleware
from app.startups.database import init_db
from app.startups.config import init_config


def init_app() -> web.Application:
    app = web.Application(middlewares=[sa_session_middleware])

    # Startups
    app.on_startup.append(init_config)
    app.on_startup.append(init_db)

    # Cleanups
    app.on_cleanup.append(close_db)

    app.add_routes([web.post("/api/v1/user", create_user_handler)])
    app.add_routes([web.post("/api/v1/wallet", create_wallet_handler)])
    return app
