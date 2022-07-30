import os
from functools import partial
from typing import Any
from unittest import mock
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from alpha import ALPHA_DOCKERHUB_IMAGE
from alpha import ALPHA_HEROKU_APP_NAME
from alpha import ALPHA_HEROKU_MAINTAINER_EMAIL
from alpha import ALPHA_OWNER
from alpha.management.commands import rebranding
from alpha.settings import Settings

pytestmark = [
    pytest.mark.unit,
]

runner = CliRunner()
run_subcommand = partial(runner.invoke, rebranding.main)


@mock.patch.dict(os.environ, {}, clear=True)
@mock.patch.object(Settings.Config, "env_file", None)
@mock.patch.object(Settings.Config, "secrets_dir", None)
def test_no_brand() -> None:
    result = run_subcommand([])
    assert result.exit_code == 2

    err = "Error: Missing argument 'BRAND'."
    assert err in result.output.strip()


@mock.patch.dict(os.environ, {}, clear=True)
@mock.patch.object(Settings.Config, "env_file", None)
@mock.patch.object(Settings.Config, "secrets_dir", None)
def test_rebrand_codeowners_full(cloned_repo_dirs: Any) -> None:
    github_username = "gh-u-beta"
    dockerhub_image = "dh-u/dh-i"
    heroku_app_name = "h-a"
    heroku_app_maintainer_email = "h-a-m-e"
    brand = "Beta"

    cmd_args = [
        f"--dockerhub-image={dockerhub_image}",
        f"--github-username={github_username}",
        f"--heroku-app-maintainer-email={heroku_app_maintainer_email}",
        f"--heroku-app-name={heroku_app_name}",
        "--yes",
        brand,
    ]

    with patch(
        "alpha.management.commands.rebranding.dirs",
        cloned_repo_dirs,
    ):
        result = run_subcommand(cmd_args)
        assert result.exit_code == 0

        target = cloned_repo_dirs.DIR_REPO / "CODEOWNERS"
        with target.open("r") as stream:
            content = stream.read()
            assert ALPHA_OWNER not in content
            assert github_username in content

        target = cloned_repo_dirs.DIR_CI_WORKFLOWS / "deploy-dockerhub.yml"
        with target.open("r") as stream:
            content = stream.read()
            assert ALPHA_DOCKERHUB_IMAGE not in content
            assert ALPHA_OWNER not in content
            assert dockerhub_image in content
            assert github_username in content

        target = cloned_repo_dirs.DIR_CI_WORKFLOWS / "deploy-heroku.yml"
        with target.open("r") as stream:
            content = stream.read()
            assert ALPHA_OWNER not in content
            assert ALPHA_HEROKU_APP_NAME not in content
            assert ALPHA_HEROKU_MAINTAINER_EMAIL not in content

        target = cloned_repo_dirs.DIR_RUN_CONFIGURATIONS / "runner.run.xml"
        with target.open("r") as stream:
            content = stream.read()
            assert "alpha" not in content
            assert brand in content

        target = (
            cloned_repo_dirs.DIR_RUN_CONFIGURATIONS / "tests - all.run.xml"
        )
        with target.open("r") as stream:
            content = stream.read()
            assert "alpha" not in content
            assert brand in content

        target = (
            cloned_repo_dirs.DIR_RUN_CONFIGURATIONS / "tests - unit.run.xml"
        )
        with target.open("r") as stream:
            content = stream.read()
            assert "alpha" not in content
            assert brand in content
