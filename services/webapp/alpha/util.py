import io
from contextlib import contextmanager
from pathlib import Path
from typing import Generator
from typing import Optional

import click
from ruamel.yaml import YAML

yaml = YAML()


def warn(message: str) -> None:
    sign = click.style(r"_!_ ", fg="yellow")
    click.echo(f"{sign} {message}")


def info(message: str) -> None:
    sign = click.style(r"(i) ", fg="bright_green")
    click.echo(f"{sign} {message}")


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


def target_to_buffer(target: Path) -> io.StringIO:
    with elastic_io(io.StringIO()) as buffer, target.open("r") as stream:
        buffer.write(stream.read())

    return buffer


def buffer_to_target(buffer: io.StringIO, target: Path) -> None:
    with elastic_io(buffer), target.open("w") as stream:
        buffer.seek(0)
        stream.write(buffer.read())
