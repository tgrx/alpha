from urllib.parse import urlsplit

from framework import config
from management.commands.abstract import ManagementCommand


class DbConfigCommand(ManagementCommand):
    name = "db-config"
    help = (
        "DB config command." " If called without arguments, displays the full DB config"
    )
    arguments = {
        "--db-name": "Prints the DB name",
        "--host": "Prints the DB host",
        "--password": "Prints the DB user's password",
        "--port": "Prints the DB port",
        "--username": "Prints the DB username",
    }

    def __call__(self):
        url = config.DATABASE_URL
        if not url:
            raise RuntimeError("database is not configured")

        url = urlsplit(url)
        path = url.path[1:]

        if self.option_is_active("--db-name"):
            print(path)
        elif self.option_is_active("--host"):
            print(url.hostname)
        elif self.option_is_active("--password"):
            print(url.password)
        elif self.option_is_active("--port"):
            print(url.port)
        elif self.option_is_active("--username"):
            print(url.username)
        else:
            full_config = f"""
                URL:     \t{url.geturl()}

                SCHEME:  \t{url.scheme}
                USERNAME:\t{url.username}
                PASSWORD:\t{url.password}
                HOST:    \t{url.hostname}
                PORT:    \t{url.port}
                DATABASE:\t{path}
            """
            print(full_config)
