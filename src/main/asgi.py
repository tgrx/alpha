from typing import Callable
from typing import Dict

import sentry_sdk

from framework.config import settings
from framework.logging import get_logger
from main.payload import HostPortT
from main.payload import PayloadT
from main.payload import RequestT
from main.payload import ScopeAsgiT
from main.payload import ScopeT

sentry_sdk.init(settings.SENTRY_DSN, traces_sample_rate=1.0)

logger = get_logger("asgi")


async def application(scope: Dict, receive: Callable, send: Callable) -> None:
    if scope["type"] == "lifespan":
        return

    path = scope["path"]
    logger.debug(f"path: {path}")

    if path.startswith("/e"):
        logger.debug(f"here goes an error ...")
        print(1 / 0)

    request = await receive()
    logger.debug(f"request: {request}")

    await send(
        {
            "headers": [
                [b"content-type", b"application/json"],
            ],
            "status": 200,
            "type": "http.response.start",
        }
    )

    payload = build_payload(scope, request)

    await send(
        {
            "body": payload.json(sort_keys=True, indent=2).encode(),
            "type": "http.response.body",
        }
    )

    logger.debug("response has been sent")


def build_payload(scope: Dict, request: Dict) -> PayloadT:
    payload = PayloadT(
        request=RequestT(
            body=request["body"].decode(),
            more_body=request["more_body"],
            type=request["type"],
        ),
        scope=ScopeT(
            asgi=ScopeAsgiT.parse_obj(scope["asgi"]),
            client=HostPortT.parse_obj(
                dict(zip(["host", "port"], scope["client"]))
            ),
            headers={k.decode(): v.decode() for k, v in scope["headers"]},
            http_version=scope["http_version"],
            method=scope["method"],
            path=scope["path"],
            query_string=scope["query_string"].decode(),
            raw_path=scope["raw_path"].decode(),
            root_path=scope["root_path"],
            scheme=scope["scheme"],
            server=HostPortT.parse_obj(
                dict(zip(["host", "port"], scope["server"]))
            ),
            type=scope["type"],
        ),
    )

    return payload
