import shutil
import sys
from pathlib import Path

import attrs
import click
from defusedxml.ElementTree import parse as parse_xml
from ruamel.yaml import YAML, CommentedMap

from alpha import ALPHA_BRAND
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

        if (node.get("name") or "").lower() == ALPHA_BRAND:
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
    """
    Rebrand .coveragerc
    """

    target = resolve_file(dirs.DIR_REPO / ".coveragerc")
    original = target_to_buffer(target)

    need_rebranding = False

    with elastic_io(original), elastic_io() as modified:
        for lo in original.readlines():
            lm = lo
            if lo.lower().strip() == f"title = {ALPHA_BRAND}":
                need_rebranding = True
                lm = f"title = {lc.brand}\n"
            modified.write(lm)

    end_if_rebranded(not need_rebranding, target)

    show_diff(target, original, modified)

    confirm(lc)

    buffer_to_target(modified, target)


@step
def rebrand_dotenv(lc: LocalContext) -> None:
    """
    Rebrand .env
    """

    assert lc.heroku_app_name, "Heroku app name is not set"

    target = resolve_file(dirs.DIR_REPO / ".env")
    original = target_to_buffer(target)

    need_rebranding = False

    line_to_change = f'HEROKU_APP_NAME="{ALPHA_HEROKU_APP_NAME}"'
    with elastic_io(original), elastic_io() as modified:
        for lo in original.readlines():
            lm = lo
            if lo.strip() == line_to_change:
                need_rebranding = True
                lm = f'HEROKU_APP_NAME="{lc.heroku_app_name}"\n'
            modified.write(lm)

    end_if_rebranded(not need_rebranding, target)

    show_diff(target, original, modified)

    confirm(lc)

    buffer_to_target(modified, target)


@step
def rebrand_docker_compose(lc: LocalContext) -> None:
    """
    Rebrand docker-compose.yml
    """

    assert lc.dockerhub_image, "Dockerhub image is not specified"

    target = resolve_file(dirs.DIR_REPO / "docker-compose.yml")

    with elastic_io(target_to_buffer(target)) as original:
        dom = yaml.load(original)

    need_rebranding = False
    brand_original = ALPHA_BRAND.lower()
    brand_modified = lc.brand.lower()

    node_services: CommentedMap = dom["services"]

    node_service_web: CommentedMap = node_services.pop(f"{brand_original}-web")
    if node_service_web:
        node_services[f"{brand_modified}-web"] = node_service_web
        need_rebranding = True
    node_service_web = node_services[f"{brand_modified}-web"]
    container_name = node_service_web["container_name"]
    if brand_original in container_name:
        need_rebranding = True
        node_service_web["container_name"] = f"{brand_modified}-web"
    depends_on = node_service_web["depends_on"]
    depends_on_modified = []
    for dep in depends_on:
        if brand_original in dep:
            need_rebranding = True
            depends_on_modified.append(dep.replace(brand_original, brand_modified))
        else:
            depends_on_modified.append(dep)
    node_service_web["depends_on"] = sorted(depends_on_modified)
    environment:dict = node_service_web["environment"]
    database_url:str = environment["DATABASE_URL"]
    if f"{brand_original}-db" in database_url:
        need_rebranding = True
        environment["DATABASE_URL"] = database_url.replace(f"{brand_original}-db", f"{brand_modified}-db")
    image: str = node_service_web["image"]
    if ALPHA_DOCKERHUB_IMAGE in image:
        need_rebranding = True
        node_service_web["image"] = image.replace(ALPHA_DOCKERHUB_IMAGE, lc.dockerhub_image)

    node_service_db: CommentedMap = node_services.pop(f"{brand_original}-db")
    if node_service_db:
        node_services[f"{brand_modified}-db"] = node_service_db
        need_rebranding = True
    node_service_db = node_services[f"{brand_modified}-db"]
    container_name = node_service_db["container_name"]
    if brand_original in container_name:
        need_rebranding = True
        node_service_db["container_name"] = f"{brand_modified}-db"
    volumes:list[str] = node_service_db["volumes"]
    volumes_modified = []
    for volume in volumes:
        if f"{brand_original}-db" in volume:
            need_rebranding = True
            volumes_modified.append(volume.replace(f"{brand_original}-db", f"{brand_modified}-db"))
        else:
            volumes_modified.append(volume)
    node_service_db["volumes"] = sorted(volumes_modified)

    node_service_dba: CommentedMap = node_services.pop(f"{brand_original}-dba")
    if node_service_dba:
        node_services[f"{lc.brand.lower()}-dba"] = node_service_dba
        need_rebranding = True
    node_service_dba = node_services[f"{lc.brand.lower()}-dba"]
    container_name = node_service_dba["container_name"]
    if brand_original in container_name:
        need_rebranding = True
        node_service_dba["container_name"] = f"{brand_modified}-dba"
    volumes: list[str] = node_service_dba["volumes"]
    volumes_modified = []
    for volume in volumes:
        if f"{brand_original}-db" in volume:
            need_rebranding = True
            volumes_modified.append(volume.replace(f"{brand_original}-db", f"{brand_modified}-db"))
        else:
            volumes_modified.append(volume)
    node_service_dba["volumes"] = sorted(volumes_modified)

    node_service_qa: CommentedMap = node_services.pop(f"{brand_original}-qa")
    if node_service_qa:
        node_services[f"{lc.brand.lower()}-qa"] = node_service_qa
        need_rebranding = True
    node_service_qa = node_services[f"{lc.brand.lower()}-qa"]
    depends_on = node_service_qa["depends_on"]
    depends_on_modified = []
    for dep in depends_on:
        if brand_original in dep:
            need_rebranding = True
            depends_on_modified.append(dep.replace(brand_original, brand_modified))
        else:
            depends_on_modified.append(dep)
    node_service_qa["depends_on"] = sorted(depends_on_modified)
    container_name = node_service_qa["container_name"]
    if brand_original in container_name:
        need_rebranding = True
        node_service_qa["container_name"] = f"{brand_modified}-qa"
    environment: dict = node_service_qa["environment"]
    database_url: str = environment["DATABASE_URL"]
    if f"{brand_original}-db" in database_url:
        need_rebranding = True
        environment["DATABASE_URL"] = database_url.replace(f"{brand_original}-db", f"{brand_modified}-db")
    test_service_url: str = environment["TEST_SERVICE_URL"]
    if f"{brand_original}-web" in test_service_url:
        need_rebranding = True
        environment["TEST_SERVICE_URL"] = test_service_url.replace(f"{brand_original}-web", f"{brand_modified}-web")
    image: str = node_service_qa["image"]
    if ALPHA_DOCKERHUB_IMAGE in image:
        need_rebranding = True
        node_service_qa["image"] = image.replace(ALPHA_DOCKERHUB_IMAGE, lc.dockerhub_image)

    node_volumes: CommentedMap = dom["volumes"]

    node_volumes_db: CommentedMap = node_volumes.pop(f"{brand_original}-db")
    if node_volumes_db:
        node_volumes[f"{lc.brand.lower()}-qa"] = node_volumes_db
        need_rebranding = True
    node_volumes_db = node_volumes[f"{lc.brand.lower()}-qa"]
    name = node_volumes_db["name"]
    if name == f"{brand_original}-db":
        need_rebranding = True
        node_volumes_db["name"] = f"{brand_modified}-db"

    end_if_rebranded(not need_rebranding, target)

    with elastic_io() as modified:
        yaml.dump(dom, modified)

    show_diff(target, original, modified)

    confirm(lc)

    buffer_to_target(modified, target)


@step
def rebrand_pyproject_toml(lc: LocalContext) -> None:
    assert lc
    f = dirs.DIR_REPO / "pyproject.toml"
    t = click.style(f.as_posix(), fg="green" if f.is_file() else "red")
    click.echo(f"rebrand {t}")


@step
def rebrand_readme_md(lc: LocalContext) -> None:
    target = resolve_file(dirs.DIR_REPO / "README.md")
    original = target_to_buffer(target)

    need_rebranding = False

    line_to_change = f"# {ALPHA_BRAND.upper()}"
    with elastic_io(original), elastic_io() as modified:
        for lo in original.readlines():
            lm = lo
            if lo.strip() == line_to_change:
                need_rebranding = True
                lm = f"# {lc.brand.upper()}\n"
            modified.write(lm)

    end_if_rebranded(not need_rebranding, target)

    show_diff(target, original, modified)

    confirm(lc)

    buffer_to_target(modified, target)


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
