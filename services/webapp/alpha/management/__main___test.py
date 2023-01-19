import os
from functools import partial
from unittest import mock

import pytest
from click.testing import CliRunner

from alpha.management import __main__
from alpha.settings import Settings

pytestmark = [
    pytest.mark.unit,
]

runner = CliRunner()
run_subcommand = partial(runner.invoke, __main__.main)


@mock.patch.dict(os.environ, {}, clear=True)
@mock.patch.object(Settings.Config, "env_file", None)
def test_main() -> None:
    result = run_subcommand([])
    assert result.exit_code == 0

    out = result.output
    assert "Usage: main [OPTIONS] COMMAND [ARGS]..." in out
    assert "Alpha Management Tool" in out
    assert "db" in out
    assert "heroku" in out


@mock.patch.dict(os.environ, {"DATABASE_URL": "x://u:p@h:1/db"}, clear=True)
@mock.patch.object(Settings.Config, "env_file", None)
def test_main_verbosity() -> None:
    result = run_subcommand(["-v", "db", "driver"])
    assert result.exit_code == 0, result.output
    out = result.output
    assert r"\|/* Alpha Management Tool *\|/*" not in out
    assert 'DB_DRIVER="x"' in out

    result = run_subcommand(["-vv", "db", "driver"])
    assert result.exit_code == 0, result.output
    out = result.output
    assert r"\|/* Alpha Management Tool *\|/*" in out
    assert 'DB_DRIVER="x"' in out
