import uvicorn

from alpha.logging import logger
from alpha.settings import Settings
from webapp.asgi import application

settings = Settings()

SERVER_RUNNING_BANNER = """
+----------------------------------------+
|             SERVER WORKS!              |
+----------------------------------------+

Visit http://{host}:{port}
Or:   {test_url}

..........................................
"""


def run() -> None:
    banner = SERVER_RUNNING_BANNER.format(
        host=settings.HOST,
        port=settings.PORT,
        test_url=settings.TEST_SERVICE_URL,
    )
    print(banner)  # noqa: T201

    try:
        uvicorn.run(
            application,
            host="0.0.0.0",  # noqa: B104,S104
            port=settings.PORT,
            reload=False,
        )
    except KeyboardInterrupt:
        logger.debug("stopping server")
    finally:
        print("server has been shut down")  # noqa: T201


if __name__ == "__main__":
    run()
