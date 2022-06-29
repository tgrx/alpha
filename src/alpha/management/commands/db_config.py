from alpha.management.commands.abstract import ManagementCommand
from alpha.settings import Settings

settings = Settings()


class DbConfigCommand(ManagementCommand):
    name = "db-config"
    help = (  # noqa: A003,VNE003
        "DB config command."
        " If called without arguments, displays the full DB config"
    )
    arguments = {
        "--db-name": "Prints the DB name",
        "--host": "Prints the DB host",
        "--password": "Prints the DB user's password",
        "--port": "Prints the DB port",
        "--username": "Prints the DB username",
    }

    def __call__(self) -> None:
        url = settings.DATABASE_URL
        if not url:
            raise RuntimeError("database is not configured")

        comps = settings.db_components_from_database_url()

        if self.option_is_active("--db-name"):
            print(comps.DB_NAME)  # noqa: T201
        elif self.option_is_active("--host"):
            print(comps.DB_HOST)  # noqa: T201
        elif self.option_is_active("--password"):
            print(comps.DB_PASSWORD)  # noqa: T201
        elif self.option_is_active("--port"):
            print(comps.DB_PORT)  # noqa: T201
        elif self.option_is_active("--username"):
            print(comps.DB_USER)  # noqa: T201
        else:
            full_config = f"""
                URL:     \t{settings.DATABASE_URL}

                SCHEME:  \t{comps.DB_DRIVER}
                USERNAME:\t{comps.DB_USER}
                PASSWORD:\t{comps.DB_PASSWORD}
                HOST:    \t{comps.DB_HOST}
                PORT:    \t{comps.DB_PORT}
                DATABASE:\t{comps.DB_NAME}
            """
            print(full_config)  # noqa: T201
