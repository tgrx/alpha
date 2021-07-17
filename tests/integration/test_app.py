import httpx
import pytest

from main.payload import PayloadT

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.functional,
]


async def test_asgi_app(asgi_client: httpx.AsyncClient) -> None:
    resp: httpx.Response = await asgi_client.get("/")
    payload = PayloadT.parse_obj(resp.json())

    assert payload.request
    assert payload.request.body == ""
    assert payload.request.more_body is True
    assert payload.request.type == "http.request"

    assert payload.scope
    assert payload.scope.asgi.spec_version is None
    assert payload.scope.asgi.version == "3.0"
    assert payload.scope.client.host == "127.0.0.1"
    assert payload.scope.client.port in range(1, 65535)
    assert payload.scope.headers["host"] == "asgi"
    assert payload.scope.headers["user-agent"] == "python-httpx/0.18.2"
    assert payload.scope.http_version == "1.1"
    assert payload.scope.method == "GET"
    assert payload.scope.path == "/"
    assert payload.scope.query_string == ""
    assert payload.scope.raw_path == "/"
    assert payload.scope.root_path == ""
    assert payload.scope.scheme == "http"
    assert payload.scope.server.host == "asgi"
    assert payload.scope.server.port is None
    assert payload.scope.type == "http"


@pytest.mark.webapp
async def test_web_app(web_client: httpx.AsyncClient) -> None:
    try:
        resp: httpx.Response = await web_client.get("/")
        payload = PayloadT.parse_obj(resp.json())

        assert payload.request
        assert payload.request.body == ""
        assert payload.request.more_body is False
        assert payload.request.type == "http.request"

        assert payload.scope
        assert payload.scope.asgi.spec_version == "2.1"
        assert payload.scope.asgi.version == "3.0"
        assert payload.scope.client.host == "127.0.0.1"
        assert payload.scope.client.port in range(1000, 65535)
        assert payload.scope.headers["host"] == "localhost:8000"
        assert payload.scope.headers["user-agent"] == "python-httpx/0.18.2"
        assert payload.scope.http_version == "1.1"
        assert payload.scope.method == "GET"
        assert payload.scope.path == "/"
        assert payload.scope.query_string == ""
        assert payload.scope.raw_path == "/"
        assert payload.scope.root_path == ""
        assert payload.scope.scheme == "http"
        assert payload.scope.server.host == "127.0.0.1"
        assert payload.scope.server.port == 8000
        assert payload.scope.type == "http"

    except (httpx.ConnectError, httpx.TimeoutException) as err:
        raise AssertionError(
            f"unable to connect to server @ {web_client.base_url}"
        ) from err
