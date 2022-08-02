import os
from functools import partial
from typing import Any
from unittest import mock
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from alpha.settings import Settings

from .rebranding import main
from .rebranding_test_checks import check_ci_deploy_dockerhub
from .rebranding_test_checks import check_ci_deploy_heroku
from .rebranding_test_checks import check_codeowners
from .rebranding_test_checks import check_coveragerc
from .rebranding_test_checks import check_docker_compose
from .rebranding_test_checks import check_dockerfile
from .rebranding_test_checks import check_dotenv
from .rebranding_test_checks import check_pyproject_toml
from .rebranding_test_checks import check_readme_md
from .rebranding_test_checks import check_run_config

pytestmark = [
    pytest.mark.unit,
]

runner = CliRunner()
run_subcommand = partial(runner.invoke, main)


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
    description = f"{brand}-description"
    dockerhub_image = f"{brand}-dockerhub-image"
    github_username = f"{brand}-github-username"
    heroku_app_maintainer_email = f"{brand}-heroku-app-maintainer-email"
    heroku_app_name = f"{brand}-heroku-app-name"
    maintainer = f"{brand}-maintainer"

    cmd_args = [
        "--yes",
        f"--description={description}",
        f"--dockerhub-image={dockerhub_image}",
        f"--github-username={github_username}",
        f"--heroku-app-maintainer-email={heroku_app_maintainer_email}",
        f"--heroku-app-name={heroku_app_name}",
        f"--maintainer={maintainer}",
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

        check_codeowners(
            cloned_repo_dirs.DIR_REPO / "CODEOWNERS",
            github_username=github_username,
        )

        check_ci_deploy_dockerhub(
            cloned_repo_dirs.DIR_CI_WORKFLOWS / "deploy-dockerhub.yml",
            dockerhub_image=dockerhub_image,
            github_username=github_username,
        )

        check_ci_deploy_heroku(
            cloned_repo_dirs.DIR_CI_WORKFLOWS / "deploy-heroku.yml",
            github_username=github_username,
            heroku_app_maintainer_email=heroku_app_maintainer_email,
            heroku_app_name=heroku_app_name,
        )

        check_run_config(
            cloned_repo_dirs.DIR_RUN_CONFIGURATIONS / "runner.run.xml",
            brand=brand,
        )

        check_run_config(
            cloned_repo_dirs.DIR_RUN_CONFIGURATIONS / "tests - all.run.xml",
            brand=brand,
        )

        check_run_config(
            cloned_repo_dirs.DIR_RUN_CONFIGURATIONS / "tests - unit.run.xml",
            brand=brand,
        )

        check_coveragerc(
            cloned_repo_dirs.DIR_REPO / ".coveragerc",
            brand=brand,
        )

        check_dotenv(
            cloned_repo_dirs.DIR_REPO / ".env",
            heroku_app_name=heroku_app_name,
        )

        check_readme_md(
            cloned_repo_dirs,
            brand=brand,
            description=description,
        )

        check_docker_compose(
            cloned_repo_dirs.DIR_REPO / "docker-compose.yml",
            brand=brand,
            dockerhub_image=dockerhub_image,
        )

        check_pyproject_toml(
            cloned_repo_dirs,
            brand=brand,
            description=description,
            maintainer=maintainer,
        )

        check_dockerfile(
            cloned_repo_dirs.DIR_REPO / "Dockerfile",
            description=description,
            maintainer=maintainer,
        )

        target = cloned_repo_dirs.DIR_DOCS
        assert not target.is_dir()

        target = cloned_repo_dirs.DIR_ALPHA
        assert not target.is_dir()

        target = cloned_repo_dirs.DIR_SRC
        assert not target.is_dir()
