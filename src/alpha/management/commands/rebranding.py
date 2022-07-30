import io
import sys
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Generator
from typing import ParamSpec

import attrs
import click
from ruamel.yaml import YAML

from alpha import ALPHA_DOCKERHUB_IMAGE
from alpha import ALPHA_OWNER
from alpha import dirs

yaml = YAML()


@attrs.define
class LocalContext:
    brand: str
    dockerfile_description: str = ""
    dockerfile_maintainer: str = ""
    dockerhub_image: str = ""
    github_username: str = ""
    heroku_app_maintainer_email: str = ""
    heroku_app_name: str = ""
    new_license: str = ""
    project_description: str = ""
    project_maintainer: str = ""
    remove_alpha: bool = False
    remove_docs: bool = False
    remove_sources: bool = False
    yes: bool = False

    def validate(self) -> None:
        err = f"the new brand={self.brand!r} is invalid: must not be empty"
        assert self.brand, err

        err = (
            f"the new brand={self.brand!r} is invalid:"
            " must differ from 'Alpha'"
        )
        assert self.brand.lower() != "alpha", err


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

    display_summary(lc)

    rebrand_codeowners(lc)
    rebrand_ci(lc)
    rebrand_run(lc)
    # deal_with_docs(lc)
    # deal_with_alpha(lc)
    # deal_with_sources(lc)
    # rebrand_coveragerc(lc)
    # rebrand_dotenv(lc)
    # rebrand_docker_compose(lc)
    # change_license(lc)
    # rebrand_pyproject_toml(lc)
    # rebrand_readme_md(lc)


def warn(text: str) -> None:
    sign = click.style(r"_!_ ", fg="yellow")
    click.echo(f"{sign} {text}")


def info(text: str) -> None:
    sign = click.style(r"(i) ", fg="bright_green")
    click.echo(f"{sign} {text}")


def confirm(lc: LocalContext) -> None:
    if lc.yes:
        return

    confirmation = input(
        click.style(
            "Agree? [please type 'agree' if yes]: ",
            fg="bright_magenta",
        )
    ).lower()

    if confirmation != "agree":
        click.echo("Stopped.")
        sys.exit(0)


class StepEnded(RuntimeError):
    pass


def end_if(cond: bool, message: str) -> None:
    if cond:
        raise StepEnded(message)


def end(message: str) -> None:
    return end_if(True, message)


P1 = ParamSpec("P1")


def step(func: Callable[P1, None]) -> Callable[P1, None]:
    @wraps(func)
    def wrapped(*args: P1.args, **kwargs: P1.kwargs) -> None:
        click.echo()
        click.secho("[*] ", fg="magenta", nl=False)

        step_name = (func.__doc__ or func.__name__).strip()
        click.echo(step_name)

        try:
            return func(*args, **kwargs)
        except AssertionError as err:
            warn(str(err))
            return None
        except StepEnded as err:
            info(str(err))
            return

    return wrapped


@contextmanager
def file_banner(target: Path) -> Generator[None, None, None]:
    len_full = 80
    len_begin = 4
    len_space = 1

    path = target.as_posix()
    len_path = len_space + len(path) + len_space

    banner_begin = "~" * len_begin
    banner_end = "~" * (len_full - len_begin - len_path)

    click.secho(f"{banner_begin} {path} {banner_end}", fg="cyan")

    try:
        yield
    finally:
        click.secho("~" * len_full, fg="cyan")
        click.echo()


@contextmanager
def elastic(buffer: io.StringIO) -> Generator[io.StringIO, None, None]:
    buffer.seek(0)
    try:
        yield buffer
    finally:
        buffer.seek(0)


def display_summary(lc: LocalContext) -> None:
    click.secho("============    REBRANDING    ============", fg="magenta")

    # TODO: use attrs.fields to get a dict and compare with default values
    for option, value in sorted(attrs.asdict(lc).items()):
        option_ = f"{option}:"
        click.echo(f"- {option_:<30} ", nl=False)

        fg = "reset"
        if value == "":
            fg = "blue"
            value = "(not set)"

        click.secho(value, fg=fg)

    confirm(lc)


@step
def rebrand_codeowners(lc: LocalContext) -> None:
    """
    Rebrand code owners
    """

    assert lc.github_username, "Github username is not specified"

    target = dirs.DIR_REPO / "CODEOWNERS"
    assert target.is_file(), f"Not a file: {target.as_posix()}"

    buffer = io.StringIO()
    lineno_modified = set()

    with target.open("r") as stream:
        for lineno, line_original in enumerate(stream.readlines(), start=1):
            tokens_original = line_original.split(" ")
            tokens_modified = []
            for token in tokens_original:
                if ALPHA_OWNER in token:
                    token = token.replace(ALPHA_OWNER, lc.github_username)
                    lineno_modified.add(lineno)
                tokens_modified.append(token)
            line_modified = " ".join(tokens_modified)
            buffer.write(f"{line_modified}\n")

    end_if(not lineno_modified, "CODEOWNERS is already rebranded.")

    with elastic(buffer), file_banner(target):
        for lineno, line_original in enumerate(buffer.readlines(), start=1):
            color = "red" if lineno in lineno_modified else "reset"
            line = f"{lineno:>4} | {line_original}"
            click.secho(line, fg=color, nl=False)

    confirm(lc)

    with elastic(buffer), target.open("w") as stream:
        stream.write(buffer.read())


@step
def rebrand_ci(lc: LocalContext) -> None:
    """
    Rebrand CI configs
    """

    rebrand_ci_deploy_dockerhub(lc)
    rebrand_ci_deploy_heroku(lc)


def rebrand_ci_deploy_dockerhub(lc: LocalContext) -> None:
    assert lc.github_username, "Github username is not specified"
    assert lc.dockerhub_image, "Dockerhub image is not specified"

    target = dirs.DIR_CI_WORKFLOWS / "deploy-dockerhub.yml"
    assert target.is_file(), f"not a file: {target.as_posix()}"

    with elastic(io.StringIO()) as buffer_original, target.open("r") as stream:
        content = stream.read()
        buffer_original.write(content)

    dom = yaml.load(content)

    line = dom["jobs"]["docker"]["if"]
    line = line.replace(ALPHA_OWNER, lc.github_username)
    dom["jobs"]["docker"]["if"] = line

    node = next(
        node
        for node in dom["jobs"]["docker"]["steps"]
        if node.get("id") == "deploy-to-dockerhub"
    )
    line = node["with"]["tags"]
    line = line.replace(ALPHA_DOCKERHUB_IMAGE, lc.dockerhub_image)
    node["with"]["tags"] = line

    with elastic(io.StringIO()) as buffer_modified:
        yaml.dump(dom, buffer_modified)

    with elastic(buffer_original), elastic(buffer_modified), file_banner(
        target
    ):
        buffers = buffer_original.readlines(), buffer_modified.readlines()
        for lineno, (line_original, line_modified) in enumerate(zip(*buffers)):
            color = "red" if line_original != line_modified else "reset"
            line = f"{lineno:>4} | {line_modified}"
            click.secho(line, fg=color, nl=False)

    confirm(lc)

    with target.open("w") as stream:
        stream.write(buffer_modified.read())


def rebrand_ci_deploy_heroku(lc: LocalContext) -> None:
    assert lc.github_username, "Github username is not specified"
    assert lc.heroku_app_name, "Heroku app name is not specified"
    assert (
        lc.heroku_app_maintainer_email
    ), "Heroku maintainer email is not specified"

    target = dirs.DIR_CI_WORKFLOWS / "deploy-heroku.yml"
    assert target.is_file(), f"not a file: {target.as_posix()}"

    with elastic(io.StringIO()) as buffer_original, target.open("r") as stream:
        content = stream.read()
        buffer_original.write(content)

    dom = yaml.load(content)

    line = dom["jobs"]["heroku"]["if"]
    line = line.replace(ALPHA_OWNER, lc.github_username)
    dom["jobs"]["heroku"]["if"] = line

    node = next(
        node
        for node in dom["jobs"]["heroku"]["steps"]
        if node.get("id") == "deploy-to-heroku"
    )

    node["with"]["heroku_app_name"] = lc.heroku_app_name
    node["with"]["heroku_email"] = lc.heroku_app_maintainer_email

    with elastic(io.StringIO()) as buffer_modified:
        yaml.dump(dom, buffer_modified)

    with elastic(buffer_original), elastic(buffer_modified), file_banner(
        target
    ):
        buffers = buffer_original.readlines(), buffer_modified.readlines()
        for lineno, (line_original, line_modified) in enumerate(zip(*buffers)):
            color = "red" if line_original != line_modified else "reset"
            line = f"{lineno:>4} | {line_modified}"
            click.secho(line, fg=color, nl=False)

    confirm(lc)

    with target.open("w") as stream:
        stream.write(buffer_modified.read())


@step
def rebrand_run(lc: LocalContext) -> None:
    assert lc

    files = {
        dirs.DIR_RUN_CONFIGURATIONS / "runner.run.xml",
        dirs.DIR_RUN_CONFIGURATIONS / "tests - all.run.xml",
        dirs.DIR_RUN_CONFIGURATIONS / "tests - unit.run.xml",
    }
    for target in sorted(files):
        target = target.resolve()
        click.secho(f"- {target.as_posix()}", fg="bright_yellow")
        assert target.is_file(), f"not a file: {target.as_posix()}"

        with elastic(io.StringIO()) as buffer_original, target.open(
            "r"
        ) as stream:
            content = stream.read()
            buffer_original.write(content)

        root = ET.fromstring(content)

        node = root.find("./configuration/module[1]")
        end_if(
            node.tag != "module" and "name" not in node.attrib,
            f"maybe malformed XML at {target.as_posix()}: node=<{node.tag} {node.attrib}>",
        )

        if node.get("name") == "alpha":
            node.set("name", lc.brand)

        with elastic(io.StringIO()) as buffer_modified:
            tree = ET.ElementTree(root)
            tree.write(buffer_modified, encoding="unicode")

        with elastic(buffer_original), elastic(buffer_modified), file_banner(
            target
        ):
            side_by_side = zip(
                buffer_original.readlines(),
                buffer_modified.readlines(),
            )
            for lineno, (line_original, line_modified) in enumerate(
                side_by_side,
                start=1,
            ):
                color = "red" if line_original != line_modified else "reset"
                line = f"{lineno:>4} | {line_modified}"
                click.secho(line, fg=color, nl=False)

        confirm(lc)

        with target.open("w") as stream:
            stream.write(buffer_modified.read())


@step
def deal_with_docs(lc: LocalContext) -> None:
    v = click.style(lc.remove_docs, fg="red" if lc.remove_docs else "green")
    click.secho(f"Remove docs? {v}")

    v = click.style(
        dirs.DIR_DOCS.as_posix(),
        fg="green" if dirs.DIR_DOCS.is_dir() else "red",
    )
    click.echo(f"deal with docs in {v}")


@step
def deal_with_alpha(lc: LocalContext) -> None:
    v = click.style(lc.remove_alpha, fg="red" if lc.remove_alpha else "green")
    click.secho(f"Remove Alpha package? {v}")

    v = click.style(
        dirs.DIR_ALPHA.as_posix(),
        fg="green" if dirs.DIR_ALPHA.is_dir() else "red",
    )
    click.echo(f"deal with Alpha in {v}")


@step
def deal_with_sources(lc: LocalContext) -> None:
    v = click.style(
        lc.remove_sources, fg="red" if lc.remove_sources else "green"
    )
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


@step
def rebrand_coveragerc(lc: LocalContext) -> None:
    assert lc
    f = dirs.DIR_REPO / ".coveragerc"
    t = click.style(f.as_posix(), fg="green" if f.is_file() else "red")
    click.echo(f"rebrand {t}")


@step
def rebrand_dotenv(lc: LocalContext) -> None:
    assert lc
    f = dirs.DIR_REPO / ".env"
    t = click.style(f.as_posix(), fg="green" if f.is_file() else "red")
    click.echo(f"rebrand {t}")


@step
def rebrand_docker_compose(lc: LocalContext) -> None:
    assert lc
    f = dirs.DIR_REPO / "docker-compose.yml"
    t = click.style(f.as_posix(), fg="green" if f.is_file() else "red")
    click.echo(f"rebrand {t}")


@step
def change_license(lc: LocalContext) -> None:
    assert lc
    f = dirs.DIR_REPO / "LICENSE"
    t = click.style(f.as_posix(), fg="green" if f.is_file() else "red")
    click.echo(f"change {t}")


@step
def rebrand_pyproject_toml(lc: LocalContext) -> None:
    assert lc
    f = dirs.DIR_REPO / "pyproject.toml"
    t = click.style(f.as_posix(), fg="green" if f.is_file() else "red")
    click.echo(f"rebrand {t}")


@step
def rebrand_readme_md(lc: LocalContext) -> None:
    assert lc
    f = dirs.DIR_REPO / "README.md"
    t = click.style(f.as_posix(), fg="green" if f.is_file() else "red")
    click.echo(f"rebrand {t}")
