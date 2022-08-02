import io
import re
import sys
from contextlib import contextmanager
from functools import partial
from functools import wraps
from pathlib import Path
from typing import Callable
from typing import Generator
from typing import Optional
from typing import ParamSpec

import attrs
import click
from ruamel.yaml import CommentedMap

from alpha import ALPHA_BRAND
from alpha import ALPHA_DOCKERHUB_IMAGE


@attrs.define
class LocalContext:
    brand: str
    description: str = ""
    dockerhub_image: str = ""
    github_username: str = ""
    heroku_app_maintainer_email: str = ""
    heroku_app_name: str = ""
    maintainer: str = ""
    remove_alpha: bool = False
    remove_docs: bool = False
    remove_sources: bool = False
    yes: bool = False

    def validate(self) -> None:
        err = f"the new brand={self.brand!r} is invalid: must not be empty"
        assert self.brand, err

        err = (
            f"the new brand={self.brand!r} is invalid:"
            f" must differ from {ALPHA_BRAND!r}"
        )
        assert self.brand.lower() != ALPHA_BRAND.lower(), err


def warn(message: str) -> None:
    sign = click.style(r"_!_ ", fg="yellow")
    click.echo(f"{sign} {message}")


def info(message: str) -> None:
    sign = click.style(r"(i) ", fg="bright_green")
    click.echo(f"{sign} {message}")


def confirm(
    lc: LocalContext,
    message: str = "",
    *,
    return_on_disagree: bool = False,
) -> bool:
    if message:
        warn(message)

    if lc.yes:
        return True

    token_apply = "yes"  # noqa: S105
    token_quit = "q"  # noqa: S105
    prompt = (
        f"Apply? "
        f"[please type {token_apply!r} to apply, "
        f"{token_quit!r} to quit]: "
    )

    choice = input(click.style(prompt, fg="bright_magenta")).lower()

    if choice == token_quit:
        click.echo("Quit.")
        sys.exit(0)

    do_apply = choice == token_apply
    assert return_on_disagree or do_apply, "Not confirmed, skip."

    return do_apply


class StepEnded(RuntimeError):
    pass


def end_if_rebranded(cond: bool, target: Path) -> None:
    msg = f"already rebranded: {target.as_posix()!r}"
    return end_if(cond, msg)


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

    click.secho(f"\n{banner_begin} {path} {banner_end}", fg="cyan")

    try:
        yield
    finally:
        click.secho("~" * len_full, fg="cyan")
        click.echo()


@contextmanager
def elastic_io(
    buffer: Optional[io.StringIO] = None,
) -> Generator[io.StringIO, None, None]:
    buffer = buffer or io.StringIO()

    buffer.seek(0)
    try:
        yield buffer
    finally:
        buffer.seek(0)


def show_diff(
    target: Path,
    original: io.StringIO,
    modified: io.StringIO,
) -> None:
    _echo = partial(click.secho, nl=False)

    with file_banner(target), elastic_io(original), elastic_io(modified):
        lines = zip(original.readlines(), modified.readlines())
        for lineno, (lo, lm) in enumerate(lines, start=1):
            eq = lo == lm
            tmpl = f"{lineno:>4} {{sep}} {{line}}"
            if eq:
                _echo(tmpl.format(sep="|", line=lo))
            else:
                _echo(tmpl.format(sep="-", line=lo), fg="red")
                _echo(tmpl.format(sep="+", line=lm), fg="green")


def resolve_file(path: Path) -> Path:
    path = path.resolve()
    assert path.is_file(), f"not a file: {path.as_posix()!r}"
    return path


def resolve_dir(path: Path) -> Path:
    path = path.resolve()
    assert path.is_dir(), f"not a dir: {path.as_posix()!r}"
    return path


def target_to_buffer(target: Path) -> io.StringIO:
    with elastic_io(io.StringIO()) as buffer, target.open("r") as stream:
        buffer.write(stream.read())

    return buffer


def buffer_to_target(buffer: io.StringIO, target: Path) -> None:
    with elastic_io(buffer), target.open("w") as stream:
        buffer.seek(0)
        stream.write(buffer.read())


class DockerComposeRebranding:
    def __init__(self, lc: LocalContext, dom: CommentedMap):
        self._dom = dom
        self._lc = lc
        self._rebranded = False

        self._cur_brand = ALPHA_BRAND.lower()

        self._new_brand = re.sub(r"\s+", "-", lc.brand.lower())
        self._new_brand = re.sub(r"[^a-z0-9-_]+", "", self._new_brand)

    @property
    def services(self) -> CommentedMap:
        services: CommentedMap = self._dom.get("services")
        assert services is not None, "malformed: no 'services:' node"
        return services

    @property
    def volumes(self) -> CommentedMap:
        volumes: CommentedMap = self._dom.get("volumes")
        assert volumes is not None, "malformed: no 'volumes:' node"
        return volumes

    def rebrand(self) -> bool:
        self._rebrand_services()
        self._rebrand_volumes()

        return self._rebranded

    def _rebrand_services(self) -> None:
        service_types = ("web", "db", "dba", "qa")

        for service_type in service_types:
            service = self._rename_service(service_type)
            self._fix_service_container_name(service)
            self._fix_service_depends_on(service)
            self._fix_service_environment(service)
            self._fix_service_image(service)
            self._fix_service_volumes(service)

    def _rebrand_volumes(self) -> None:
        cur = f"{self._cur_brand}-db"
        new = f"{self._new_brand}-db"
        db = self.__rename_node(self.volumes, cur, new)
        self.__rebrand_str_attr(db, "name", cur, new)

    def _rename_service(self, service_type: str) -> CommentedMap:
        cur = f"{self._cur_brand}-{service_type}"
        new = f"{self._new_brand}-{service_type}"

        service = self.__rename_node(self.services, cur, new)

        return service

    def _fix_service_container_name(self, service: CommentedMap) -> None:
        self.__rebrand_str_attr(
            service,
            "container_name",
            self._cur_brand,
            self._new_brand,
        )

    def _fix_service_depends_on(self, service: CommentedMap) -> None:
        self.__rebrand_list_attr(service, "depends_on")

    def _fix_service_environment(self, service: CommentedMap) -> None:
        cur: CommentedMap = service.get("environment")
        if cur is None:
            return

        self.__rebrand_str_attr(
            cur,
            "DATABASE_URL",
            f"{self._cur_brand}-db",
            f"{self._new_brand}-db",
        )
        self.__rebrand_str_attr(
            cur,
            "TEST_SERVICE_URL",
            f"{self._cur_brand}-web",
            f"{self._new_brand}-web",
        )

    def _fix_service_image(self, service: CommentedMap) -> None:
        assert self._lc.dockerhub_image, "no dockerhub image specified"
        self.__rebrand_str_attr(
            service,
            "image",
            ALPHA_DOCKERHUB_IMAGE,
            self._lc.dockerhub_image,
        )

    def _fix_service_volumes(self, service: CommentedMap) -> None:
        self.__rebrand_list_attr(service, "volumes")

    def __rename_node(
        self,
        parent: CommentedMap,
        current_name: str,
        new_name: str,
    ) -> CommentedMap:
        node = parent.pop(current_name)
        if node is not None:
            self._rebranded = True
            parent[new_name] = node

        node = parent.get(new_name)

        errmsg = f"node '{new_name}:' not found. Contact support."
        assert node is not None, errmsg

        errmsg = (
            f"node '{new_name}:' invalid type={type(node)}. "
            f"Contact support."
        )
        assert isinstance(node, CommentedMap), errmsg

        return node

    def __rebrand_str_attr(
        self,
        node: CommentedMap,
        attr: str,
        cur: str,
        new: str,
    ) -> None:
        cur_value: str = node.get(attr)
        if not cur_value:
            return

        if cur in cur_value:
            self._rebranded = True
            new_value = cur_value.replace(cur, new)
            node[attr] = new_value

    def __rebrand_list_attr(self, node: CommentedMap, attr: str) -> None:
        cur: list = node.get(attr) or []
        if not cur:
            return

        new = []
        for item in cur:
            if isinstance(item, str):  # noqa: SIM102
                if self._cur_brand in item:
                    self._rebranded = True
                    item = item.replace(self._cur_brand, self._new_brand)
            new.append(item)

        node[attr] = sorted(new)
