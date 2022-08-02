import os
from configparser import ConfigParser
from functools import partial
from pathlib import Path
from typing import Any
from unittest import mock
from unittest.mock import patch

import pytest
import tomlkit
from click.testing import CliRunner
from defusedxml.ElementTree import parse as parse_xml
from dockerfile_parse import DockerfileParser
from dotenv import dotenv_values

from alpha import ALPHA_DESCRIPTION
from alpha import ALPHA_DOCKERHUB_IMAGE
from alpha import ALPHA_HEROKU_APP_NAME
from alpha import ALPHA_MAINTAINER
from alpha import ALPHA_MAINTAINER_EMAIL
from alpha import ALPHA_OWNER
from alpha.management.commands import rebranding
from alpha.management.commands.rebranding_util import resolve_file
from alpha.settings import Settings
from alpha.util import yaml

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
            assert f"heroku_app_name: {ALPHA_HEROKU_APP_NAME}" not in content
            assert f"heroku_app_name: {heroku_app_name}" in content
            assert f"heroku_email: {ALPHA_MAINTAINER_EMAIL}" not in content
            assert f"heroku_email: {heroku_app_maintainer_email}" in content

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
            cloned_repo_dirs,
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


def check_run_config(
    target: Path,
    *,
    brand: str,
) -> None:
    target = resolve_file(target)
    with target.open("r") as stream:
        tree = parse_xml(
            stream,
            forbid_dtd=True,
            forbid_entities=True,
            forbid_external=True,
        )

        node = tree.find("./configuration/module[1]")
        assert node is not None
        assert node.attrib["name"] == brand


def check_coveragerc(
    target: Path,
    *,
    brand: str,
) -> None:
    target = resolve_file(target)
    rc = ConfigParser()
    rc.read(target)
    assert rc["html"]["title"] == brand


def check_dotenv(
    target: Path,
    *,
    heroku_app_name: str,
) -> None:
    target = resolve_file(target)
    env = dotenv_values(target)
    assert env["HEROKU_APP_NAME"] == heroku_app_name


def check_dockerfile(
    target: Path,
    *,
    description: str,
    maintainer: str,
) -> None:
    target = resolve_file(target)
    dockerfile = DockerfileParser(target.as_posix())
    assert ALPHA_DESCRIPTION not in dockerfile.content
    assert ALPHA_MAINTAINER not in dockerfile.content
    labels = dockerfile.labels
    assert labels["description"] == description
    assert labels["org.opencontainers.image.authors"] == maintainer


def check_pyproject_toml(
    dirs: Any,
    *,
    maintainer: str,
    description: str,
    brand: str,
) -> None:
    target = resolve_file(dirs.DIR_REPO / "pyproject.toml")
    with target.open("r") as stream:
        dom: Any = tomlkit.load(stream)
        poetry = dom["tool"]["poetry"]
        assert maintainer in poetry["authors"]
        assert poetry["description"] == description
        assert poetry["name"] == brand


def check_docker_compose(
    dirs: Any,
    *,
    brand: str,
    dockerhub_image: str,
) -> None:
    target = resolve_file(dirs.DIR_REPO / "docker-compose.yml")
    with target.open("r") as stream:
        dom = yaml.load(stream)

        services = dom["services"]

        web = services.get(f"{brand}-web")
        assert web is not None
        assert web["container_name"] == f"{brand}-web"
        assert f"{brand}-db" in web["depends_on"]
        assert f"{brand}-db" in web["environment"]["DATABASE_URL"]
        assert web["image"] == f"{dockerhub_image}:dev"

        db = services.get(f"{brand}-db")
        assert db is not None
        assert db["container_name"] == f"{brand}-db"
        assert any(f"{brand}-db" in volume for volume in db["volumes"])

        dba = services.get(f"{brand}-dba")
        assert dba is not None
        assert dba["container_name"] == f"{brand}-dba"
        assert any(f"{brand}-db" in volume for volume in dba["volumes"])

        qa = services.get(f"{brand}-qa")
        assert qa is not None
        assert qa["container_name"] == f"{brand}-qa"
        assert f"{brand}-web" in qa["depends_on"]
        assert f"{brand}-db" in qa["environment"]["DATABASE_URL"]
        assert f"{brand}-web" in qa["environment"]["TEST_SERVICE_URL"]
        assert qa["image"] == f"{dockerhub_image}:dev"

        volumes = dom["volumes"]

        db = volumes.get(f"{brand}-db")
        assert db is not None
        assert db["name"] == f"{brand}-db"


def check_readme_md(
    dirs: Any,
    *,
    brand: str,
    description: str,
) -> None:
    target = resolve_file(dirs.DIR_REPO / "README.md")
    with target.open("r") as stream:
        content = stream.read()
        assert f"# {brand.upper()}" in content
        assert description in content
