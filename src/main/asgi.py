from typing import Callable
from typing import Dict

import sentry_sdk

from framework import config
from framework.logging import get_logger

sentry_sdk.init(config.SENTRY_DSN, traces_sample_rate=1.0)

HTML_CONTENT = """
<!DOCTYPE html>
<html>
    <head>
        <title>Alpha</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>Project Alpha</h1>
        <hr>
        <p>This is a template project.</p>
        <p>
            <h2>Scope</h2>
            <p>{scope}</p>
        </p>
        <p>
            <h2>Request</h2>
            <p>{request}</p>
        </p>
    </body>
</html>
"""

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
                [b"content-type", b"text/html"],
            ],
        }
    )

    payload = HTML_CONTENT.format(request=request, scope=scope)

    await send(
        {
            "type": "http.response.body",
            "body": payload.encode(),
        }
    )

    logger.debug(f"response has been sent")
