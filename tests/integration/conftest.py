from typing import Generator

import httpx
import pytest

from framework.config import settings
from main.asgi import application

TIMEOUT = 4


@pytest.fixture(scope="function")
async def asgi_client() -> Generator[httpx.AsyncClient, None, None]:
    async with httpx.AsyncClient(
        app=application,
        base_url="http://asgi",
        timeout=TIMEOUT,
    ) as client:
        yield client


@pytest.fixture(scope="function")
async def web_client() -> Generator[httpx.AsyncClient, None, None]:
    async with httpx.AsyncClient(
        base_url=settings.TEST_SERVICE_URL,
        timeout=TIMEOUT,
    ) as client:
        yield client
