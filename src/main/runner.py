import uvicorn

from alpha.logging import logger
from alpha.settings import Settings
from main.asgi import application

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
    logger.info(banner)

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
        logger.info("server has been shut down")


if __name__ == "__main__":
    run()
