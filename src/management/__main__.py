import argparse
import sys

from management.commands import COMMANDS


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        title="commands",
    )

    for command_name, command in COMMANDS.items():
        command_parser = subparsers.add_parser(command_name, help=command.help)
        if command.arguments:
            group = command_parser.add_mutually_exclusive_group(
                required=command.required
            )
            for key, help_ in command.arguments.items():
                dest = command.dest(key)
                group.add_argument(
                    key,
                    action="store_true",
                    dest=dest,
                    help=help_,
                )

    try:
        args = parser.parse_args()
    except TypeError:
        import traceback

        traceback.print_exc()
        parser.print_help()
        sys.exit(1)

    cmd_cls = COMMANDS.get(args.command)
    cmd = cmd_cls(args)
    cmd()


if __name__ == "__main__":
    main()
