from contextlib import asynccontextmanager
from typing import AsyncIterator
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

import asyncpg
import sentry_sdk

from alpha.logging import logger
from alpha.settings import Settings
from main.custom_types import DbSetting
from main.custom_types import HostPortT
from main.custom_types import PayloadT
from main.custom_types import RequestT
from main.custom_types import ScopeAsgiT
from main.custom_types import ScopeT

settings = Settings()

sentry_sdk.init(settings.SENTRY_DSN, traces_sample_rate=1.0)


@asynccontextmanager
async def get_db_connection() -> AsyncIterator:
    conn: Optional[asyncpg.Connection] = None
    log = logger.bind(db=settings.DATABASE_URL)
    try:
        log.debug("attempt to connect to db")
        conn = await asyncpg.connect(settings.DATABASE_URL)
        yield conn
    except Exception:
        log.exception("database is not available")
        raise
    finally:
        log.debug("closing the connection")
        if conn is not None:
            await conn.close()


async def get_db_settings() -> List[DbSetting]:
    sql = """
        SELECT
            trim(short_desc || ' ' || coalesce(extra_desc, '')) as description,
            name,
            setting,
            unit
        FROM
            pg_settings
        ;
    """

    db_settings: List[DbSetting] = []

    try:
        logger.debug("get db settings", sql=sql)
        conn: asyncpg.Connection
        async with get_db_connection() as conn:
            stmt = await conn.prepare(sql)
            records = await stmt.fetch()

        db_settings = [DbSetting.parse_obj(rec) for rec in records]

    except (OSError, asyncpg.PostgresError) as err:
        logger.exception("db exception", err=err)

    return db_settings


async def application(scope: Dict, receive: Callable, send: Callable) -> None:
    if scope["type"] == "lifespan":
        return

    path = scope["path"]
    logger.debug("path: %s", path)

    if path.startswith("/e"):
        logger.debug("here goes an error ...")
        print(1 / 0)  # noqa: T201

    request = await receive()
    logger.debug("request: %s", request)

    await send(
        {
            "headers": [
                [b"content-type", b"application/json"],
            ],
            "status": 200,
            "type": "http.response.start",
        }
    )

    db_settings = await get_db_settings()
    payload = build_payload(scope, request, db_settings)

    await send(
        {
            "body": payload.json(sort_keys=True, indent=2).encode(),
            "type": "http.response.body",
        }
    )

    logger.debug("response has been sent")


def build_payload(
    scope: Dict,
    request: Dict,
    db_settings: List[DbSetting],
) -> PayloadT:
    payload = PayloadT(
        db_settings=db_settings,
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
