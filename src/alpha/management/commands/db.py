import attrs
import click

from alpha.management.common import ManagementContext
from alpha.settings import DatabaseSettings


@attrs.define
class LocalContext:
    verbose: int = attrs.field(default=0)
    ds: DatabaseSettings = attrs.field(factory=DatabaseSettings)


pass_local_context = click.make_pass_decorator(LocalContext)


@click.group()
@click.option(
    "--from-url",
    help="Uses given URL as DATABASE_URL.",
    metavar="<URL>",
    type=str,
)
@click.pass_context
def main(ctx: click.Context, *, from_url: str = "") -> None:
    """
    Database Management Tool
    """

    mc: ManagementContext = ctx.ensure_object(ManagementContext)

    db_url = from_url or mc.settings.DATABASE_URL
    if not db_url:
        raise click.UsageError("DATABASE_URL is not configured")

    ds = DatabaseSettings(
        DATABASE_URL=db_url,
    ).db_components_from_database_url()

    ctx.obj = LocalContext(
        ds=ds,
        verbose=mc.verbose,
    )


@main.command(name="url")
@pass_local_context
def echo_url(lc: LocalContext) -> None:
    """
    Displays the URL.
    """

    echo_db_component(lc, "DATABASE_URL")


@main.command(name="driver")
@pass_local_context
def echo_driver(lc: LocalContext) -> None:
    """
    Displays the driver (schema, protocol).
    """

    echo_db_component(lc, "DB_DRIVER")


@main.command(name="user")
@pass_local_context
def echo_user(lc: LocalContext) -> None:
    """
    Displays the user.
    """

    echo_db_component(lc, "DB_USER")


@main.command(name="password")
@pass_local_context
def echo_password(lc: LocalContext) -> None:
    """
    Displays the password. BEWARE: password is visible!
    """

    echo_db_component(lc, "DB_PASSWORD")


@main.command(name="host")
@click.option(
    "-p",
    "--port",
    default=False,
    help="Include port in output.",
    is_flag=True,
)
@pass_local_context
def echo_host(lc: LocalContext, *, port: bool = False) -> None:
    """
    Displays the hostname.
    """

    msg = lc.ds.DB_HOST
    if port:
        msg = f"{msg}:{lc.ds.DB_PORT}"

    if lc.verbose:
        field = "DB_HOST"
        msg = click.style(msg, fg=_fields_colors[field])
        msg = f'{field}="{msg}"'

    click.echo(msg)


@main.command(name="port")
@pass_local_context
def echo_port(lc: LocalContext) -> None:
    """
    Displays the port.
    """

    echo_db_component(lc, "DB_PORT")


@main.command(name="name")
@pass_local_context
def echo_name(lc: LocalContext) -> None:
    """
    Displays the database name.
    """

    echo_db_component(lc, "DB_NAME")


_fields_colors = {
    "DATABASE_URL": "blue",
    "DB_DRIVER": "magenta",
    "DB_HOST": "yellow",
    "DB_NAME": "green",
    "DB_PASSWORD": "blue",
    "DB_PORT": "yellow",
    "DB_USER": "cyan",
}


def echo_db_component(lc: LocalContext, field: str) -> None:
    msg = getattr(lc.ds, field)

    if lc.verbose:
        msg = click.style(msg, fg=_fields_colors[field])
        msg = f'{field}="{msg}"'

    click.echo(msg)
