import attrs
import click


@attrs.define
class ManagementContext:
    verbose: int = attrs.field(default=0)


pass_mgmt_context = click.make_pass_decorator(ManagementContext, ensure=True)


def show_ads() -> None:
    blink = click.style(r"*\|/*", fg="red", blink=True, bold=True)
    ads = click.style("Alpha Management Tool", fg="bright_red")
    click.secho(f"{blink} {ads} {blink}\n", bg="black")
