import os
from functools import partial
from typing import Generator
from unittest import mock

import pytest
from click.testing import CliRunner

from alpha.management.commands.db import main
from alpha.management.common import ManagementContext
from alpha.settings import Settings

pytestmark = [
    pytest.mark.unit,
]


@pytest.fixture
def run_subcommand() -> Generator[partial, None, None]:
    runner = CliRunner()
    subcommand = partial(runner.invoke, main)
    yield subcommand


@mock.patch.dict(os.environ, {}, clear=True)
@mock.patch.object(Settings.Config, "env_file", None)
def test_db_not_configured(run_subcommand: partial) -> None:
    result = run_subcommand(["name"])
    assert result.exit_code == 2
    assert "Error: DATABASE_URL is not configured" in result.output


driver = "postgresql"
host = "host"
name = "somedb"
password = "0xfeeddead"  # noqa: S105
port = 1234
user = "user"
url = f"{driver}://{user}:{password}@{host}:{port}/{name}"

test_env = {
    "DATABASE_URL": url,
}


@mock.patch.dict(os.environ, test_env, clear=True)
@mock.patch.object(Settings.Config, "env_file", None)
@pytest.mark.parametrize(
    "subcommand,expected",
    [
        ("driver", driver),
        ("host", host),
        ("name", name),
        ("password", password),
        ("port", port),
        ("url", url),
        ("user", user),
    ],
)
def test_subcommands(
    run_subcommand: partial,
    subcommand: str,
    expected: str,
) -> None:
    result = run_subcommand([subcommand])
    assert result.exit_code == 0
    assert result.output.strip() == str(expected)


@mock.patch.dict(os.environ, test_env, clear=True)
@mock.patch.object(Settings.Config, "env_file", None)
def test_verbose(run_subcommand: partial) -> None:
    result = run_subcommand(["name"], obj=ManagementContext(verbose=1))
    assert result.exit_code == 0
    assert result.output.strip() == f'DB_NAME="{name}"'


@mock.patch.dict(os.environ, test_env, clear=True)
@mock.patch.object(Settings.Config, "env_file", None)
@pytest.mark.parametrize(
    "options,verbose,expected",
    [
        (["--port"], 0, f"{host}:{port}"),
        (["--port"], 1, f'DB_HOST="{host}:{port}"'),
        (["-p"], 0, f"{host}:{port}"),
        (["-p"], 1, f'DB_HOST="{host}:{port}"'),
        ([], 0, host),
        ([], 1, f'DB_HOST="{host}"'),
    ],
)
def test_subcommand_host(
    run_subcommand: partial,
    options: list[str],
    verbose: int,
    expected: str,
) -> None:
    mc = ManagementContext(verbose=verbose)
    result = run_subcommand(["host"] + options, obj=mc)
    assert result.exit_code == 0
    assert result.output.strip() == expected
