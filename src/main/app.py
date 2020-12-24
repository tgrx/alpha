import uvicorn

from framework import config
from framework.logging import get_logger
from main.asgi import application

SERVER_RUNNING_BANNER = """
+----------------------------------------+
|             SERVER WORKS!              |
+----------------------------------------+

Visit http://{host}:{port}

..........................................
"""

logger = get_logger("app")


def run():
    banner = SERVER_RUNNING_BANNER.format(host=config.HOST, port=config.PORT)
    logger.info(banner)

    try:
        uvicorn.run(application, host="0.0.0.0", port=config.PORT)
    except KeyboardInterrupt:
        logger.debug("stopping server")
    finally:
        logger.info("server has been shut down")


if __name__ == "__main__":
    run()
