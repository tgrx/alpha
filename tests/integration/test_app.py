import httpx
import pytest

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.functional,
]


def validate_root_response(resp: httpx.Response):
    assert resp.status_code == 200
    assert resp.json() == {}


async def test_asgi_app(asgi_client: httpx.AsyncClient):
    resp: httpx.Response = await asgi_client.get("/")
    validate_root_response(resp)


@pytest.mark.webapp
async def test_web_app(web_client: httpx.AsyncClient):
    try:
        resp: httpx.Response = await web_client.get("/")
        validate_root_response(resp)
    except (httpx.ConnectError, httpx.TimeoutException) as err:
        raise AssertionError(
            f"unable to connect to server @ {web_client.base_url}"
        ) from err
