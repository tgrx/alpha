import io
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

from alpha import ALPHA_BRAND


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

    token_apply = "yes"
    token_quit = "q"

    choice = input(
        click.style(
            f"Apply? [please type {token_apply!r} to apply, {token_quit!r} to quit]: ",
            fg="bright_magenta",
        )
    ).lower()

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
