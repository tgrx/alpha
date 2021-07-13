import json
from typing import Callable
from typing import Dict

import sentry_sdk

from framework.config import settings
from framework.logging import get_logger

sentry_sdk.init(settings.SENTRY_DSN, traces_sample_rate=1.0)

logger = get_logger("asgi")


async def application(scope: Dict, receive: Callable, send: Callable):
    path = scope["path"]
    logger.debug(f"path: {path}")

    if path.startswith("/e"):
        logger.debug(f"here goes an error ...")
        print(1 / 0)

    request = await receive()
    logger.debug(f"request: {request}")

    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [
                [b"content-type", b"application/json"],
            ],
        }
    )

    payload = {}

    await send(
        {
            "type": "http.response.body",
            "body": json.dumps(payload).encode(),
        }
    )

    logger.debug(f"response has been sent")
