import uvloop
from aiohttp import web

from app.app import init_app


def main() -> None:
    uvloop.install()
    app = init_app()
    web.run_app(app, host="0.0.0.0", port=8080)  # noqa: WPS432 Found magic number: 8080


if __name__ == "__main__":
    main()
