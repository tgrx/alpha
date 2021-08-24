from typing import Optional

import httpx
import pytest

from main.custom_types import PayloadT

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.functional,
]

TCP_PORTS_RANGE = range(1000, 65535)


def validate_payload(
    payload: PayloadT,
    *,
    request__more_body: bool = False,
    scope__asgi__spec_version: Optional[str] = None,
    scope__client__port_range: range = TCP_PORTS_RANGE,
    scope__headers__host: str = "asgi",
    scope__server__host: str = "asgi",
    scope__server__port: Optional[int] = None,
) -> None:
    assert payload.request
    assert payload.request.body == ""
    assert payload.request.more_body is request__more_body
    assert payload.request.type == "http.request"

    assert payload.scope
    assert payload.scope.asgi.spec_version == scope__asgi__spec_version
    assert payload.scope.asgi.version == "3.0"
    assert payload.scope.client.host == "127.0.0.1"
    assert payload.scope.client.port in scope__client__port_range
    assert payload.scope.headers["host"] == scope__headers__host
    assert payload.scope.headers["user-agent"] == "python-httpx/0.19.0"
    assert payload.scope.http_version == "1.1"
    assert payload.scope.method == "GET"
    assert payload.scope.path == "/"
    assert payload.scope.query_string == ""
    assert payload.scope.raw_path == "/"
    assert payload.scope.root_path == ""
    assert payload.scope.scheme == "http"
    assert payload.scope.server.host == scope__server__host
    assert payload.scope.server.port == scope__server__port
    assert payload.scope.type == "http"


async def test_asgi_app(asgi_client: httpx.AsyncClient) -> None:
    resp: httpx.Response = await asgi_client.get("/")
    payload = PayloadT.parse_obj(resp.json())

    validate_payload(
        payload,
        request__more_body=True,
        scope__client__port_range=range(123, 124),
    )

    with pytest.raises(ZeroDivisionError):
        await asgi_client.get("/e")


@pytest.mark.webapp
async def test_web_app(web_client: httpx.AsyncClient) -> None:
    try:
        resp: httpx.Response = await web_client.get("/")
        payload = PayloadT.parse_obj(resp.json())
        validate_payload(
            payload,
            scope__asgi__spec_version="2.1",
            scope__headers__host="localhost:8000",
            scope__server__host="127.0.0.1",
            scope__server__port=8000,
        )
    except (httpx.ConnectError, httpx.TimeoutException) as err:
        raise AssertionError(
            f"unable to connect to server @ {web_client.base_url}"
        ) from err


@pytest.mark.webapp
async def test_error_handling_webapp(web_client: httpx.AsyncClient) -> None:
    resp: httpx.Response = await web_client.get("/e")
    assert resp.status_code == 500
