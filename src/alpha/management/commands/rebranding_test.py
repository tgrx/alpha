import os
from functools import partial
from typing import Generator
from unittest import mock

import pytest
from click.testing import CliRunner

from alpha.management.commands import rebranding
from alpha.settings import Settings

pytestmark = [
    pytest.mark.unit,
]


@pytest.fixture
def run_subcommand() -> Generator[partial, None, None]:
    runner = CliRunner()
    subcommand = partial(runner.invoke, rebranding.main)
    yield subcommand


@mock.patch.dict(os.environ, {}, clear=True)
@mock.patch.object(Settings.Config, "env_file", None)
@mock.patch.object(Settings.Config, "secrets_dir", None)
def test_no_brand(
    run_subcommand: partial,
) -> None:
    result = run_subcommand([])
    assert result.exit_code == 2

    err = "Error: Missing argument 'BRAND'."
    assert err in result.output.strip()
