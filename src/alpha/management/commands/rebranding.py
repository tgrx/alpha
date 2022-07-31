from typing import Any

import click

from alpha.management.commands import rebranding_steps
from alpha.management.commands.rebranding_util import LocalContext


@click.command()
@click.option(
    "--dockerfile-description",
    default="",
    help="Dockerfile description",
)
@click.option(
    "--dockerfile-maintainer",
    default="",
    help="Dockerfile maintainer",
)
@click.option(
    "--dockerhub-image",
    default="",
    help="Docker Hub repo/image",
)
@click.option(
    "--github-username",
    default="",
    help="Github user name",
)
@click.option(
    "--heroku-app-maintainer-email",
    default="",
    help="Heroku app maintainer email",
)
@click.option(
    "--heroku-app-name",
    default="",
    help="Heroku app name",
)
@click.option(
    "--new-license",
    default="",
    help="Change license - DANGEROUS",
)
@click.option(
    "--project-description",
    default="",
    help="Project description",
)
@click.option(
    "--project-maintainer",
    default="",
    help="Project maintainer",
)
@click.option(
    "--remove-alpha",
    default=False,
    help="Remove Alpha package - DANGEROUS",
    is_flag=True,
)
@click.option(
    "--remove-docs",
    default=False,
    help="Remove existing docs, leaving the stub",
    is_flag=True,
)
@click.option(
    "--remove-sources",
    default=False,
    help="Remove all sources - DANGEROUS",
    is_flag=True,
)
@click.option(
    "--yes",
    default=False,
    help="Apply changes without asking for confirmation",
    is_flag=True,
)
@click.argument("brand", nargs=1)
def main(**kwargs: Any) -> None:
    """
    Rebranding Tool
    """

    lc = LocalContext(**kwargs)

    try:
        lc.validate()
    except AssertionError as err:
        raise click.UsageError(str(err)) from err

    steps = (
        rebranding_steps.display_summary,
        rebranding_steps.modify_license,
        rebranding_steps.rebrand_ci_deploy_dockerhub,
        rebranding_steps.rebrand_ci_deploy_heroku,
        rebranding_steps.rebrand_codeowners,
        rebranding_steps.rebrand_coveragerc,
        rebranding_steps.rebrand_docker_compose,
        rebranding_steps.rebrand_dotenv,
        rebranding_steps.rebrand_pyproject_toml,
        rebranding_steps.rebrand_readme_md,
        rebranding_steps.rebrand_run,
        rebranding_steps.remove_project_paths,
    )

    for step_func in steps:
        step_func(lc)
