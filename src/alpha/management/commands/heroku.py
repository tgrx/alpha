from typing import Any
from typing import Optional

import click
import httpx

from alpha.management.common import ManagementContext
from alpha.management.common import json_dumps
from alpha.management.common import pass_mgmt_context
from alpha.settings import Settings

settings = Settings()
HEROKU_API_URL = "https://api.heroku.com/apps"


@click.command(
    help=(
        "Heroku management command."
        " If called without arguments, prints an app config in JSON format."
        " Both HEROKU_APP_NAME and HEROKU_API_KEY MUST be configured."
    )
)
@click.option(
    "--configure",
    is_flag=True,
    help="Configures your app on Heroku.",
    default=False,
)
@pass_mgmt_context
def command_heroku(
    mc: ManagementContext,
    *,
    configure: bool = False,
) -> None:
    validate()

    if configure:
        return do_configure(mc)

    return do_output_config(mc)


def do_configure(mc: ManagementContext) -> None:
    payload = {
        name: value
        for name, value in {
            "PYTHONPATH": "src",
            "SENTRY_DSN": settings.SENTRY_DSN,
        }.items()
        if value is not None
    }

    response = call_api(
        mc,
        method="patch",
        path="config-vars",
        payload=payload,
    )
    payload = response.json()
    msg = json_dumps(payload)
    click.echo(msg)


def do_output_config(mc: ManagementContext) -> None:
    response = call_api(mc)
    payload = response.json()
    msg = json_dumps(payload)
    click.echo(msg)


def call_api(
    mc: ManagementContext,
    *,
    method: str = "get",
    path: str = "",
    payload: Optional[dict] = None,
) -> httpx.Response:
    headers = {
        "Accept": "application/vnd.heroku+json; version=3",
        "Authorization": f"Bearer {settings.HEROKU_API_TOKEN}",
        "Content-Type": "application/json",
    }

    url = f"{HEROKU_API_URL}/{settings.HEROKU_APP_NAME}/{path}"

    meth = getattr(httpx, method.lower())

    meth_kwargs = {
        "headers": headers,
    }
    if payload:
        meth_kwargs["json"] = payload

    spam_request(
        mc,
        method=method,
        headers=headers,
        payload=payload,
        url=url,
    )

    response: httpx.Response = meth(url, **meth_kwargs)

    if response.status_code != 200:
        msg = (
            f"unable to get app info: {response.status_code}\n"
            f"{response.content!r}"
        )
        raise click.UsageError(msg)

    return response


def validate() -> None:
    if not settings.HEROKU_APP_NAME:
        raise click.UsageError("HEROKU_APP_NAME is not configured.")

    if not settings.HEROKU_API_TOKEN:
        raise click.UsageError(
            "HEROKU_API_TOKEN is not set: "
            "see https://help.heroku.com/PBGP6IDE/"
        )


def spam_request(
    mc: ManagementContext,
    *,
    headers: dict[str, Any],
    method: str,
    payload: Any = None,
    url: str,
) -> None:
    if not mc.verbose:
        return

    click.secho(f"{method.upper()} {url}", fg="magenta")
    if mc.verbose > 1:
        if mc.verbose > 2:
            for header, value in headers.items():
                header = click.style(header, fg="bright_blue")
                value = click.style(value, fg="blue")
                msg = f"{header}: {value}"
                click.echo(msg)
        if payload:
            msg = json_dumps(payload)
            msg = f"\n{msg}"
            click.secho(msg, fg="cyan")

        click.echo("")
