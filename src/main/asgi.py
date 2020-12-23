import json
from typing import Callable
from typing import Dict

import sentry_sdk

from framework.util.settings import get_setting

sentry_sdk.init(get_setting("SENTRY_DSN"), traces_sample_rate=1.0)


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
    </body>
</html>
"""


async def application(scope: Dict, receive: Callable, send: Callable):
    path = scope["path"]
    method = scope["method"]

    if path.startswith("/e"):
        print(1 / 0)

    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [
                [b"content-type", b"text/html"],
            ],
        }
    )

    await send(
        {
            "type": "http.response.body",
            "body": HTML_CONTENT.encode(),
        }
    )
