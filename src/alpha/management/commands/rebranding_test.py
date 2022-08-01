import os
from functools import partial
from typing import Any
from unittest import mock
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from alpha import ALPHA_BRAND
from alpha import ALPHA_DOCKERHUB_IMAGE
from alpha import ALPHA_HEROKU_APP_NAME
from alpha import ALPHA_HEROKU_MAINTAINER_EMAIL
from alpha import ALPHA_OWNER
from alpha.management.commands import rebranding
from alpha.management.commands.rebranding_util import resolve_file
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
    brand = "beta"
    dockerhub_image = f"{brand}-dockerhub-image"
    github_username = f"{brand}-github-username"
    heroku_app_maintainer_email = f"{brand}-heroku-app-maintainer-email"
    heroku_app_name = f"{brand}-heroku-app-name"

    cmd_args = [
        "--yes",
        f"--dockerhub-image={dockerhub_image}",
        f"--github-username={github_username}",
        f"--heroku-app-maintainer-email={heroku_app_maintainer_email}",
        f"--heroku-app-name={heroku_app_name}",
        f"--remove-alpha",  # noqa: F541
        f"--remove-docs",  # noqa: F541
        f"--remove-sources",  # noqa: F541
        brand,
    ]

    with patch(
        "alpha.management.commands.rebranding_steps.dirs",
        cloned_repo_dirs,
    ):
        result = run_subcommand(cmd_args)
        assert result.exit_code == 0

        target = resolve_file(cloned_repo_dirs.DIR_REPO / "CODEOWNERS")
        with target.open("r") as stream:
            content = stream.read()
            assert f"*   @{ALPHA_OWNER}" not in content
            assert f"*   @{github_username}" in content

        target = resolve_file(
            cloned_repo_dirs.DIR_CI_WORKFLOWS / "deploy-dockerhub.yml"
        )
        with target.open("r") as stream:
            content = stream.read()
            assert f"if: github.actor == '{ALPHA_OWNER}'" not in content
            assert f"if: github.actor == '{github_username}'" in content
            assert (
                f"{ALPHA_DOCKERHUB_IMAGE}:${{{{ steps.build-args.outputs.version }}}}"  # noqa: E501
                not in content
            )
            assert f"{ALPHA_DOCKERHUB_IMAGE}:latest" not in content
            assert (
                f"{dockerhub_image}:${{{{ steps.build-args.outputs.version }}}}"  # noqa: E501
                in content
            )
            assert f"{dockerhub_image}:latest" in content

        target = resolve_file(
            cloned_repo_dirs.DIR_CI_WORKFLOWS / "deploy-heroku.yml"
        )
        with target.open("r") as stream:
            content = stream.read()
            assert f"if: github.actor == '{ALPHA_OWNER}'" not in content
            assert f"if: github.actor == '{github_username}'" in content
            assert f'heroku_app_name: "{ALPHA_HEROKU_APP_NAME}"' not in content
            assert f'heroku_app_name: "{heroku_app_name}"' not in content
            assert (
                f'heroku_email: "{ALPHA_HEROKU_MAINTAINER_EMAIL}"'
                not in content
            )
            assert (
                f'heroku_email: "{heroku_app_maintainer_email}"' not in content
            )

        target = resolve_file(
            cloned_repo_dirs.DIR_RUN_CONFIGURATIONS / "runner.run.xml"
        )
        with target.open("r") as stream:
            content = stream.read()
            assert f'<module name="{ALPHA_BRAND.lower()}" />' not in content
            assert f'<module name="{brand}" />' in content

        target = resolve_file(
            cloned_repo_dirs.DIR_RUN_CONFIGURATIONS / "tests - all.run.xml"
        )
        with target.open("r") as stream:
            content = stream.read()
            assert f'<module name="{ALPHA_BRAND.lower()}" />' not in content
            assert f'<module name="{brand}" />' in content

        target = resolve_file(
            cloned_repo_dirs.DIR_RUN_CONFIGURATIONS / "tests - unit.run.xml"
        )
        with target.open("r") as stream:
            content = stream.read()
            assert f'<module name="{ALPHA_BRAND.lower()}" />' not in content
            assert f'<module name="{brand}" />' in content

        target = resolve_file(cloned_repo_dirs.DIR_REPO / ".coveragerc")
        with target.open("r") as stream:
            content = stream.read()
            assert f"title = {ALPHA_BRAND.capitalize()}" not in content
            assert f"title = {brand}" in content

        target = resolve_file(cloned_repo_dirs.DIR_REPO / ".env")
        with target.open("r") as stream:
            content = stream.read()
            assert f'HEROKU_APP_NAME="{ALPHA_HEROKU_APP_NAME}"' not in content
            assert f'HEROKU_APP_NAME="{heroku_app_name}"' in content

        target = resolve_file(cloned_repo_dirs.DIR_REPO / "README.md")
        with target.open("r") as stream:
            content = stream.read()
            assert f"# {ALPHA_BRAND.upper()}" not in content
            assert f"# {brand.upper()}" in content

        target = resolve_file(cloned_repo_dirs.DIR_REPO / "docker-compose.yml")
        with target.open("r") as stream:
            content = stream.read()
            assert ALPHA_DOCKERHUB_IMAGE not in content
            assert dockerhub_image in content
            assert f"container_name: {ALPHA_BRAND.lower()}-db" not in content
            assert f"container_name: {ALPHA_BRAND.lower()}-dba" not in content
            assert f"container_name: {ALPHA_BRAND.lower()}-qa" not in content
            assert f"container_name: {ALPHA_BRAND.lower()}-web" not in content
            assert f"container_name: {brand.lower()}-db" in content
            assert f"container_name: {brand.lower()}-dba" in content
            assert f"container_name: {brand.lower()}-qa" in content
            assert f"container_name: {brand.lower()}-web" in content
            assert f"{ALPHA_BRAND.lower()}-db" not in content
            assert f"{ALPHA_BRAND.lower()}-dba" not in content
            assert f"{ALPHA_BRAND.lower()}-qa" not in content
            assert f"{ALPHA_BRAND.lower()}-web" not in content
            assert f"{brand.lower()}-db" in content
            assert f"{brand.lower()}-dba" in content
            assert f"{brand.lower()}-qa" in content
            assert f"{brand.lower()}-web" in content

        target = cloned_repo_dirs.DIR_DOCS
        assert not target.is_dir()

        target = cloned_repo_dirs.DIR_ALPHA
        assert not target.is_dir()

        target = cloned_repo_dirs.DIR_SRC
        assert not target.is_dir()
