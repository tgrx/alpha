import shutil
import sys
from pathlib import Path

import attrs
import click
from defusedxml.ElementTree import parse as parse_xml
from ruamel.yaml import YAML

from alpha import ALPHA_DOCKERHUB_IMAGE
from alpha import ALPHA_HEROKU_APP_NAME
from alpha import ALPHA_HEROKU_MAINTAINER_EMAIL
from alpha import ALPHA_OWNER
from alpha import dirs
from alpha.management.commands.rebranding_util import LocalContext
from alpha.management.commands.rebranding_util import buffer_to_target
from alpha.management.commands.rebranding_util import confirm
from alpha.management.commands.rebranding_util import elastic_io
from alpha.management.commands.rebranding_util import end_if_rebranded
from alpha.management.commands.rebranding_util import info
from alpha.management.commands.rebranding_util import resolve_dir
from alpha.management.commands.rebranding_util import resolve_file
from alpha.management.commands.rebranding_util import show_diff
from alpha.management.commands.rebranding_util import step
from alpha.management.commands.rebranding_util import target_to_buffer
from alpha.management.commands.rebranding_util import warn

yaml = YAML()


def display_summary(lc: LocalContext) -> None:
    click.secho("============    REBRANDING    ============", fg="magenta")

    for option, value in sorted(attrs.asdict(lc).items()):
        option_ = f"{option}:"
        click.echo(f"- {option_:<30} ", nl=False)

        fg = "reset"
        if value == "":
            fg = "blue"
            value = "(not set)"

        click.secho(value, fg=fg)

    go = confirm(lc, return_on_disagree=True)
    if not go:
        sys.exit(0)


@step
def rebrand_codeowners(lc: LocalContext) -> None:
    """
    Rebrand code owners
    """

    assert lc.github_username, "Github username is not specified"

    target = resolve_file(dirs.DIR_REPO / "CODEOWNERS")

    need_rebranding = False

    with elastic_io(
        target_to_buffer(target)
    ) as original, elastic_io() as modified:
        for line_original in original.readlines():
            tokens_original = line_original.split(" ")
            tokens_modified = []
            for token in tokens_original:
                if f"@{ALPHA_OWNER}" in token:
                    token = token.replace(ALPHA_OWNER, lc.github_username)
                    need_rebranding = True
                tokens_modified.append(token)
            line_modified = " ".join(tokens_modified)
            modified.write(f"{line_modified}\n")

    end_if_rebranded(not need_rebranding, target)

    show_diff(target, original, modified)

    confirm(lc)

    buffer_to_target(modified, target)


@step
def rebrand_ci_deploy_dockerhub(lc: LocalContext) -> None:
    """
    Rebrand deploy-dockerhub.yml
    """

    assert lc.github_username, "Github username is not specified"
    assert lc.dockerhub_image, "Dockerhub image is not specified"

    target = resolve_file(dirs.DIR_CI_WORKFLOWS / "deploy-dockerhub.yml")

    with elastic_io(target_to_buffer(target)) as original:
        dom = yaml.load(original)

    need_rebranding = False

    line = dom["jobs"]["docker"]["if"]
    if ALPHA_OWNER in line:
        need_rebranding = True
        line = line.replace(ALPHA_OWNER, lc.github_username)
        dom["jobs"]["docker"]["if"] = line

    node = next(
        node
        for node in dom["jobs"]["docker"]["steps"]
        if node.get("id") == "deploy-to-dockerhub"
    )

    line = node["with"]["tags"]
    if ALPHA_DOCKERHUB_IMAGE in line:
        need_rebranding = True
        line = line.replace(ALPHA_DOCKERHUB_IMAGE, lc.dockerhub_image)
        node["with"]["tags"] = line

    end_if_rebranded(not need_rebranding, target)

    with elastic_io() as modified:
        yaml.dump(dom, modified)

    show_diff(target, original, modified)

    confirm(lc)

    buffer_to_target(modified, target)


@step
def rebrand_ci_deploy_heroku(lc: LocalContext) -> None:
    """
    Rebrand deploy-heroku.yml
    """

    assert lc.github_username, "Github username is not specified"
    assert lc.heroku_app_name, "Heroku app name is not specified"
    assert (
        lc.heroku_app_maintainer_email
    ), "Heroku maintainer email is not specified"

    target = resolve_file(dirs.DIR_CI_WORKFLOWS / "deploy-heroku.yml")

    with elastic_io(target_to_buffer(target)) as original:
        dom = yaml.load(original)

    need_rebranding = False

    line = dom["jobs"]["heroku"]["if"]
    if ALPHA_OWNER in line:
        need_rebranding = True
        line = line.replace(ALPHA_OWNER, lc.github_username)
        dom["jobs"]["heroku"]["if"] = line

    node = next(
        node
        for node in dom["jobs"]["heroku"]["steps"]
        if node.get("id") == "deploy-to-heroku"
    )

    line = node["with"]["heroku_app_name"]
    if ALPHA_HEROKU_APP_NAME in line:
        need_rebranding = True
        node["with"]["heroku_app_name"] = lc.heroku_app_name

    line = node["with"]["heroku_email"]
    if ALPHA_HEROKU_MAINTAINER_EMAIL in line:
        need_rebranding = True
        node["with"]["heroku_email"] = lc.heroku_app_maintainer_email

    end_if_rebranded(not need_rebranding, target)

    with elastic_io() as modified:
        yaml.dump(dom, modified)

    show_diff(target, original, modified)

    confirm(lc)

    buffer_to_target(modified, target)


@step
def rebrand_run(lc: LocalContext) -> None:
    """
    Rebrand Pycharm run configurations
    """

    files = {
        dirs.DIR_RUN_CONFIGURATIONS / "runner.run.xml",
        dirs.DIR_RUN_CONFIGURATIONS / "tests - all.run.xml",
        dirs.DIR_RUN_CONFIGURATIONS / "tests - unit.run.xml",
    }

    for target in sorted(files):
        target = resolve_file(target.resolve())

        with elastic_io(target_to_buffer(target)) as original:
            tree = parse_xml(
                original,
                forbid_dtd=True,
                forbid_entities=True,
                forbid_external=True,
            )

        node = tree.find("./configuration/module[1]")
        assert node is not None, f"malformed XML in {target.as_posix()!r}"

        err_msg_attrs = ", ".join(
            f"{a}={v!r}" for a, v in sorted(node.attrib.items())
        )
        err_msg = (
            f"maybe malformed XML at {target.as_posix()}: "
            f"node=<{node.tag} {err_msg_attrs}>"
        )
        assert node.tag == "module" and "name" in node.attrib, err_msg

        if node.get("name") == "alpha":
            node.set("name", lc.brand)
        else:
            info(f"already rebranded: {target.as_posix()!r}")
            continue

        with elastic_io() as modified:
            tree.write(modified, encoding="unicode")

        show_diff(target, original, modified)

        do_rebrand = confirm(lc, return_on_disagree=True)
        if do_rebrand:
            buffer_to_target(modified, target)


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
def modify_license(lc: LocalContext) -> None:
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


@step
def remove_project_paths(lc: LocalContext) -> None:
    paths: dict[Path, bool] = {
        dirs.DIR_ALPHA: lc.remove_alpha or lc.remove_sources,
        dirs.DIR_DOCS: lc.remove_docs,
        dirs.DIR_SRC: lc.remove_sources,
        dirs.DIR_TESTS: lc.remove_sources,
    }

    for path, to_be_removed in paths.items():
        try:
            target = resolve_dir(path)
        except AssertionError:
            warn(f"not found, skip: {path.as_posix()!r}")
            continue

        if not to_be_removed:
            info(f"{target.as_posix()!r} stays")
            continue

        do_remove = confirm(
            lc,
            f"dir will be removed: {target.as_posix()!r}",
            return_on_disagree=True,
        )
        if do_remove:
            shutil.rmtree(target, ignore_errors=True)
