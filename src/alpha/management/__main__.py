import click

from alpha.management.commands.db import command_db
from alpha.management.commands.heroku import command_heroku
from alpha.management.common import ManagementContext
from alpha.management.common import show_ads


@click.group
@click.option("-v", "--verbose", count=True)
@click.pass_context
def main(ctx: click.Context, *, verbose: int = 0) -> None:
    mctx = ManagementContext(verbose=verbose)
    ctx.obj = mctx

    if mctx.verbose > 1:  # user requests spam!
        show_ads()


main.add_command(command_db, "db")
main.add_command(command_heroku, "heroku")

if __name__ == "__main__":
    main()
