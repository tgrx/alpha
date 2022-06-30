from functools import partial

import click

from alpha.management.common import ManagementContext
from alpha.management.common import pass_mgmt_context
from alpha.settings import DatabaseSettings
from alpha.settings import Settings

settings = Settings()

_full_config = """
    URL:     \t{DATABASE_URL}

    DRIVER:  \t{DB_DRIVER}

    USERNAME:\t{DB_USER}
    PASSWORD:\t{DB_PASSWORD}
    HOST:    \t{DB_HOST}
    PORT:    \t{DB_PORT}
    DATABASE:\t{DB_NAME}
"""

_fields_colors = {
    "DB_HOST": "bright_red",
    "DB_NAME": "yellow",
    "DB_PASSWORD": "blue",
    "DB_PORT": "red",
    "DB_USER": "bright_blue",
}


@click.command(
    help="Prints requested DB components or full DB config",
    name="db",
)
@click.option(
    "-d",
    "--db",
    default=False,
    help="Prints the DB name.",
    is_flag=True,
)
@click.option(
    "-h",
    "--host",
    default=False,
    help="Prints the DB host.",
    is_flag=True,
)
@click.option(
    "-p",
    "--port",
    default=False,
    help="Prints the DB port.",
    is_flag=True,
)
@click.option(
    "-w",
    "--password",
    default=False,
    help="Prints the DB password.",
    is_flag=True,
)
@click.option(
    "-u",
    "--username",
    default=False,
    help="Prints the DB username.",
    is_flag=True,
)
@pass_mgmt_context
def command_db(
    mc: ManagementContext,
    *,
    db: bool = False,
    host: bool = False,
    password: bool = False,
    port: bool = False,
    username: bool = False,
) -> None:
    url = settings.DATABASE_URL
    if not url:
        raise click.UsageError("DATABASE_URL is not configured")

    comps = settings.db_components_from_database_url()

    echo = partial(echo_value, mc, comps)

    echo_what = {
        "DB_USER": username,
        "DB_PASSWORD": password,
        "DB_HOST": host,
        "DB_PORT": port,
        "DB_NAME": db,
    }

    fields = [field for field, need in echo_what.items() if need]
    for field in fields:
        echo(field)

    if not fields:
        value = _full_config.format(
            DATABASE_URL=comps.DATABASE_URL,
            DB_DRIVER=comps.DB_DRIVER,
            DB_HOST=comps.DB_HOST,
            DB_NAME=comps.DB_NAME,
            DB_PASSWORD=comps.DB_PASSWORD,
            DB_PORT=comps.DB_PORT,
            DB_USER=comps.DB_USER,
        )
        click.echo(value)


def echo_value(
    mc: ManagementContext, comps: DatabaseSettings, field: str
) -> None:
    value = getattr(comps, field)
    if mc.verbose:
        value = click.style(value, fg=_fields_colors[field])
        value = f"{field:<12}: {value}"
    click.echo(value)
