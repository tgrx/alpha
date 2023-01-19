import multiprocessing as mp
from typing import NoReturn
from typing import Type
from urllib.parse import urlsplit

import pydantic as pd
from pydantic import error_wrappers as pdew


def build_config() -> Type[pd.BaseConfig]:
    class _DefaultConfig(pd.BaseConfig):
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

    return _DefaultConfig


class DatabaseSettings(pd.BaseSettings):
    DATABASE_URL: str | None = None
    DB_DRIVER: str | None = None
    DB_HOST: str | None = None
    DB_NAME: str | None = pd.Field(env=["DB_NAME", "POSTGRES_DB"])
    DB_PASSWORD: str | None = pd.Field(
        env=["DB_PASSWORD", "POSTGRES_PASSWORD"]
    )
    DB_PORT: int | None = None
    DB_USER: str | None = pd.Field(env=["DB_USER", "POSTGRES_USER"])

    Config = build_config()

    def database_url_from_db_components(self) -> str:
        """
        Returns database url composed from database components.
        Does not update self DATABASE_URL.
        """

        def fail_validation(error_message: str) -> NoReturn:
            raise pdew.ValidationError(
                errors=[
                    pdew.ErrorWrapper(
                        exc=ValueError(error_message),
                        loc="schema",
                    )
                ],
                model=DatabaseSettings,
            )

        if not self.DB_DRIVER:
            fail_validation("db driver MUST be set")

        if not self.DB_HOST and self.DB_PORT:
            fail_validation("db host MUST be set when port is set")

        if not self.DB_USER and self.DB_PASSWORD:
            fail_validation("db user MUST be set when password is set")

        netloc = ":".join(map(str, filter(bool, (self.DB_HOST, self.DB_PORT))))
        userinfo = ":".join(
            filter(bool, (self.DB_USER, self.DB_PASSWORD))  # type: ignore  # noqa: E501
        )

        if not netloc and userinfo:
            fail_validation("netloc MUST be set when userinfo is set")

        authority = "@".join(filter(bool, (userinfo, netloc)))

        url = f"{self.DB_DRIVER}://{authority}"

        if self.DB_NAME:
            url = f"{url}/{self.DB_NAME}"

        return url

    def db_components_from_database_url(self) -> "DatabaseSettings":
        """
        Returns new instance with components extracted from DATABASE_URL.
        Returns self copy if DATABASE_URL is not set.
        Does not update self components.
        """

        if not self.DATABASE_URL:
            return DatabaseSettings()

        components = urlsplit(self.DATABASE_URL)

        return DatabaseSettings(
            DATABASE_URL=self.DATABASE_URL,
            DB_DRIVER=components.scheme,
            DB_HOST=components.hostname,
            DB_NAME=components.path[1:],
            DB_PASSWORD=components.password,
            DB_PORT=components.port,
            DB_USER=components.username,
        )


class Settings(DatabaseSettings):
    __name__ = "Settings"  # noqa: VNE003

    Config = build_config()

    HEROKU_API_TOKEN: str | None = None
    HEROKU_APP_NAME: str | None = None
    HOST: str = "localhost"
    MODE_DEBUG: bool = False
    PORT: int = 8000
    REQUEST_TIMEOUT: int = 30
    SENTRY_DSN: str | None = None
    TEST_SERVICE_URL: str = "http://localhost:8000"
    WEB_CONCURRENCY: int = mp.cpu_count() * 2 + 1
