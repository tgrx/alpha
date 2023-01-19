import os
from functools import partial
from typing import Any
from typing import Generator
from unittest import mock

import orjson
import pytest
from click.testing import CliRunner

from alpha.management.commands import heroku
from alpha.management.common import ManagementContext
from alpha.management.common import json_dumps
from alpha.settings import Settings

pytestmark = [
    pytest.mark.unit,
]


@pytest.fixture
def run_subcommand() -> Generator[partial, None, None]:
    runner = CliRunner()
    subcommand = partial(runner.invoke, heroku.main)
    yield subcommand


@mock.patch.dict(os.environ, {}, clear=True)
@mock.patch.object(Settings.Config, "env_file", None)
def test_app_not_configured_name(
    run_subcommand: partial,
) -> None:
    result = run_subcommand(["app"])
    assert result.exit_code == 2

    err = "Error: HEROKU_APP_NAME is not configured."
    assert err in result.output.strip()


@mock.patch.dict(os.environ, {"HEROKU_APP_NAME": "xxx"}, clear=True)
@mock.patch.object(Settings.Config, "env_file", None)
def test_app_not_configured_token(
    run_subcommand: partial,
) -> None:
    result = run_subcommand(["app"])
    assert result.exit_code == 2

    err = (
        "Error: HEROKU_API_TOKEN is not set:"
        " see https://help.heroku.com/PBGP6IDE/"
    )
    assert err in result.output.strip()


name = "xxx"
token = "000000"  # noqa: S105

test_env: dict[str, str] = {
    "HEROKU_API_TOKEN": token,
    "HEROKU_APP_NAME": name,
}


@mock.patch.dict(os.environ, test_env, clear=True)
@mock.patch.object(Settings.Config, "env_file", None)
def test_app(
    httpx_mock: Any,
    run_subcommand: partial,
) -> None:
    response_payload = {"x": "y"}

    httpx_mock.add_response(
        json=response_payload,
        match_content=None,
        match_headers={
            "Authorization": f"Bearer {token}",
        },
        method="GET",
        url=f"https://api.heroku.com/apps/{name}/",
    )

    result = run_subcommand(["app"])
    assert result.exit_code == 0

    assert json_dumps(response_payload) in result.output


sentry = "sentry"


@mock.patch.dict(os.environ, test_env | {"SENTRY_DSN": sentry}, clear=True)
@mock.patch.object(Settings.Config, "env_file", None)
def test_set_config_vars(
    httpx_mock: Any,
    run_subcommand: partial,
) -> None:
    response_payload = {
        "response": "payload",
    }

    request_payload = {
        "PYTHONPATH": "src",
        "SENTRY_DSN": sentry,
    }

    httpx_mock.add_response(
        json=response_payload,
        match_content=orjson.dumps(
            request_payload,
            option=orjson.OPT_SORT_KEYS,
        ),
        match_headers={
            "Authorization": f"Bearer {token}",
        },
        method="patch",
        url=f"https://api.heroku.com/apps/{name}/config-vars",
    )

    result = run_subcommand(["set-config-vars"])
    assert result.exit_code == 0

    assert json_dumps(response_payload) in result.output


@mock.patch.dict(os.environ, test_env | {"SENTRY_DSN": sentry}, clear=True)
@mock.patch.object(Settings.Config, "env_file", None)
def test_set_config_vars_dry_run(
    httpx_mock: Any,
    run_subcommand: partial,
) -> None:
    request_payload = {
        "PYTHONPATH": "src",
        "SENTRY_DSN": sentry,
    }

    result = run_subcommand(["set-config-vars", "--dry-run"])

    assert result.exit_code == 0
    assert json_dumps(request_payload) in result.output
    assert not httpx_mock.get_requests()

    mc = ManagementContext(verbose=1)
    result = run_subcommand(["set-config-vars", "--dry-run"], obj=mc)
    assert result.exit_code == 0
    assert json_dumps(request_payload) in result.output
    assert "DRY RUN!" in result.output
    assert not httpx_mock.get_requests()
