import click

from alpha import dirs


@click.command()
@click.option("--dockerfile-description", help="Dockerfile description", default="")
@click.option("--dockerfile-maintainer", help="Dockerfile maintainer", default="")
@click.option("--dockerhub-image", help="Docker Hub repo/image", default="")
@click.option("--github-username", help="Github user name", default="")
@click.option("--heroku-app-maintainer-email", help="Heroku app maintainer email", default="")
@click.option("--heroku-app-name", help="Heroku app name", default="")
@click.option("--new-license", help="Change license - DANGEROUS", default="")
@click.option("--project-description", help="Project description", default="")
@click.option("--project-maintainer", help="Project maintainer", default="")
@click.option("--remove-alpha", is_flag=True, help="Remove Alpha package - DANGEROUS", default=False)
@click.option("--remove-docs", is_flag=True, help="Remove existing docs, leaving the stub", default=False)
@click.option("--remove-sources", is_flag=True, help="Remove all sources - DANGEROUS", default=False)
@click.argument("brand", nargs=1)
def main(
        *,
        brand: str,
        dockerfile_description: str = "",
        dockerfile_maintainer: str = "",
        dockerhub_image: str = "",
        github_username: str = "",
        heroku_app_maintainer_email: str = "",
        heroku_app_name: str = "",
        new_license: str = "",
        project_description: str = "",
        project_maintainer: str = "",
        remove_alpha: bool = False,
        remove_docs: bool = False,
        remove_sources: bool = False,
) -> None:
    """
    Rebranding Tool
    """

    def xxx(n, v):
        v = click.style(v, fg="green")
        click.echo(f"{n}: {v}")

    click.secho("rebranding!", fg="red")
    xxx("brand", brand)
    xxx("GitHub username", github_username)
    xxx("DockerHub image", dockerhub_image)
    xxx("Heroku app", heroku_app_name)
    xxx("Heroku maintainer", heroku_app_maintainer_email)

    rebrand_ci()
    rebrand_run()
    deal_with_docs(remove_docs)
    deal_with_alpha(remove_alpha)
    deal_with_sources(remove_sources)
    rebrand_coveragerc()
    rebrand_dotenv()
    rebrand_docker_compose()
    change_license()
    rebrand_pyproject_toml()
    rebrand_readme_md()


def rebrand_ci():
    files = {
        dirs.DIR_CI / 'CODEOWNERS',
        dirs.DIR_CI_WORKFLOWS / 'deploy-dockerhub.yml',
        dirs.DIR_CI_WORKFLOWS / 'deploy-heroku.yml',
    }
    for i, f in enumerate(sorted(files), start=1):
        f = f.resolve()
        fn = click.style(f.as_posix(), fg="green" if f.is_file() else "red")
        click.echo(f"{i}. rebrand {fn}")


def rebrand_run():
    files = {
        dirs.DIR_RUN_CONFIGURATIONS / 'app.run.xml',
        dirs.DIR_RUN_CONFIGURATIONS / 'tests - all.run.xml',
        dirs.DIR_RUN_CONFIGURATIONS / 'tests - unit.run.xml',
    }
    for i, f in enumerate(sorted(files), start=1):
        f = f.resolve()
        fn = click.style(f.as_posix(), fg="green" if f.is_file() else "red")
        click.echo(f"{i}. rebrand {fn}")


def deal_with_docs(remove_docs: bool = False):
    v = click.style(remove_docs, fg="red" if remove_docs else "green")
    click.secho(f"Remove docs? {v}")

    v = click.style(
        dirs.DIR_DOCS.as_posix(),
        fg="green" if dirs.DIR_DOCS.is_dir() else "red",
    )
    click.echo(f"deal with docs in {v}")


def deal_with_alpha(remove_alpha: bool = False):
    v = click.style(remove_alpha, fg="red" if remove_alpha else "green")
    click.secho(f"Remove Alpha package? {v}")

    v = click.style(
        dirs.DIR_ALPHA.as_posix(),
        fg="green" if dirs.DIR_ALPHA.is_dir() else "red",
    )
    click.echo(f"deal with Alpha in {v}")


def deal_with_sources(remove_sources: bool = False):
    v = click.style(remove_sources, fg="red" if remove_sources else "green")
    click.secho(f"Remove all sources? {v}")

    v = click.style(
        dirs.DIR_SRC.as_posix(),
        fg="green" if dirs.DIR_SRC.is_dir() else "red",
    )
    click.echo(f"deal with sources in {v}")

    v = click.style(
        dirs.DIR_TESTS.as_posix(),
        fg="green" if dirs.DIR_TESTS.is_dir() else "red",
    )
    click.echo(f"deal with tests in {v}")


def rebrand_coveragerc():
    f = dirs.DIR_REPO / ".coveragerc"
    f = click.style(
        f.as_posix(),
        fg="green" if f.is_file() else "red"
    )
    click.echo(f"rebrand {f}")


def rebrand_dotenv():
    f = dirs.DIR_REPO / ".env"
    f = click.style(
        f.as_posix(),
        fg="green" if f.is_file() else "red"
    )
    click.echo(f"rebrand {f}")


def rebrand_docker_compose():
    f = dirs.DIR_REPO / "docker-compose.yml"
    f = click.style(
        f.as_posix(),
        fg="green" if f.is_file() else "red"
    )
    click.echo(f"rebrand {f}")


def change_license():
    f = dirs.DIR_REPO / "LICENSE"
    f = click.style(
        f.as_posix(),
        fg="green" if f.is_file() else "red"
    )
    click.echo(f"change {f}")


def rebrand_pyproject_toml():
    f = dirs.DIR_REPO / "pyproject.toml"
    f = click.style(
        f.as_posix(),
        fg="green" if f.is_file() else "red"
    )
    click.echo(f"rebrand {f}")


def rebrand_readme_md():
    f = dirs.DIR_REPO / "README.md"
    f = click.style(
        f.as_posix(),
        fg="green" if f.is_file() else "red"
    )
    click.echo(f"rebrand {f}")
