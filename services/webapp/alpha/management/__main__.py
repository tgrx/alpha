import click

from alpha.management.commands import db
from alpha.management.commands import heroku
from alpha.management.common import ManagementContext
from alpha.management.common import show_ads


@click.group
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Can be used many times to increase verbosity (spam).",
)
@click.pass_context
def main(ctx: click.Context, *, verbose: int = 0) -> None:
    """
    Alpha Management Tool
    """

    mc = ManagementContext(verbose=verbose)
    ctx.obj = mc

    if mc.verbose > 1:  # user requests spam!  # pragma: no cover
        show_ads()


main.add_command(db.main, "db")
main.add_command(heroku.main, "heroku")

if __name__ == "__main__":
    main()
