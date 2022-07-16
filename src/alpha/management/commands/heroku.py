from typing import Any
from typing import Optional

import click
import httpx
import orjson

from alpha.management.common import ManagementContext
from alpha.management.common import json_dumps
from alpha.management.common import pass_mgmt_context

HEROKU_API_URL = "https://api.heroku.com/apps"


@click.group()
@pass_mgmt_context
def main(mc: ManagementContext) -> None:
    """
    Heroku Management Tool

    Both HEROKU_APP_NAME and HEROKU_API_KEY MUST be configured.
    """

    if not mc.settings.HEROKU_APP_NAME:
        raise click.UsageError("HEROKU_APP_NAME is not configured.")

    if not mc.settings.HEROKU_API_TOKEN:
        raise click.UsageError(
            "HEROKU_API_TOKEN is not set: "
            "see https://help.heroku.com/PBGP6IDE/"
        )


@main.command(name="set-config-vars")
@click.option(
    "--dry-run",
    default=False,
    help="Displays the new config vars without patching.",
    is_flag=True,
    show_default="off, config vars will be changed",
)
@pass_mgmt_context
def set_config_vars(mc: ManagementContext, *, dry_run: bool = False) -> None:
    """
    Sets config vars for app on Heroku.
    """

    payload = {
        name: value
        for name, value in {
            "PYTHONPATH": "src",
            "SENTRY_DSN": mc.settings.SENTRY_DSN,
        }.items()
        if value is not None
    }

    if dry_run:
        click.echo(json_dumps(payload))
        if mc.verbose:
            click.secho("\nDRY RUN!", fg="yellow")
        return

    response = call_api(
        mc,
        method="patch",
        path="config-vars",
        payload=payload,
    )
    payload = response.json()
    msg = json_dumps(payload)
    click.echo(msg)


@main.command(name="app")
@pass_mgmt_context
def echo_app_config(mc: ManagementContext) -> None:
    """
    Displays app config in JSON format.
    """

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
        "Authorization": f"Bearer {mc.settings.HEROKU_API_TOKEN}",
        "Content-Type": "application/json",
    }

    url = f"{HEROKU_API_URL}/{mc.settings.HEROKU_APP_NAME}/{path}"

    meth = getattr(httpx, method.lower())

    meth_kwargs: dict[str, Any] = {
        "headers": headers,
    }
    if payload:
        meth_kwargs["content"] = orjson.dumps(
            payload,
            option=orjson.OPT_SORT_KEYS,
        )

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
