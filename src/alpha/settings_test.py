import json
import os
from multiprocessing import cpu_count
from unittest import mock

import pytest
from pydantic import ValidationError

from alpha.settings import DatabaseSettings
from alpha.settings import Settings

pytestmark = [
    pytest.mark.unit,
]


@mock.patch.dict(os.environ, {}, clear=True)
@mock.patch.object(Settings.Config, "env_file", None)
@mock.patch.object(Settings.Config, "secrets_dir", None)
def test_default_settings() -> None:
    settings = Settings()
    nr_cpus = 2 * cpu_count() + 1

    assert settings.DATABASE_URL is None
    assert settings.DB_DRIVER is None
    assert settings.DB_HOST is None
    assert settings.DB_NAME is None
    assert settings.DB_PASSWORD is None
    assert settings.DB_PORT is None
    assert settings.DB_USER is None
    assert settings.HOST == "localhost"
    assert settings.MODE_DEBUG is False
    assert settings.PORT == 8000
    assert settings.SENTRY_DSN is None
    assert settings.WEB_CONCURRENCY == nr_cpus
    with pytest.raises(ValidationError):
        settings.database_url_from_db_components()
    assert settings.db_components_from_database_url() == DatabaseSettings()


@mock.patch.dict(os.environ, {}, clear=True)
def test_database_url_from_db_components() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings().database_url_from_db_components()

    err = json.loads(exc_info.value.json())
    assert isinstance(err, list)
    assert err == [
        {
            "loc": ["schema"],
            "msg": "db driver MUST be set",
            "type": "value_error",
        }
    ]

    url = Settings(
        DB_DRIVER="postgresql+asyncpg",
    ).database_url_from_db_components()
    assert url == "postgresql+asyncpg://"

    url = Settings(
        DB_DRIVER="sqlite",
        DB_HOST="localhost",
    ).database_url_from_db_components()
    assert url == "sqlite://localhost"

    url = Settings(
        DB_DRIVER="sqlite",
        DB_NAME=":memory:",
    ).database_url_from_db_components()
    assert url == "sqlite:///:memory:"

    with pytest.raises(ValidationError) as exc_info:
        Settings(
            DB_DRIVER="sqlite",
            DB_USER="user",
        ).database_url_from_db_components()
    err = json.loads(exc_info.value.json())
    assert isinstance(err, list)
    assert err == [
        {
            "loc": ["schema"],
            "msg": "netloc MUST be set when userinfo is set",
            "type": "value_error",
        }
    ]

    with pytest.raises(ValidationError) as exc_info:
        Settings(
            DB_DRIVER="postgresql",
            DB_PORT="5432",
        ).database_url_from_db_components()
    err = json.loads(exc_info.value.json())
    assert isinstance(err, list)
    assert err == [
        {
            "loc": ["schema"],
            "msg": "db host MUST be set when port is set",
            "type": "value_error",
        }
    ]

    with pytest.raises(ValidationError) as exc_info:
        Settings(  # noqa: S106,B106
            DB_DRIVER="postgresql",
            DB_PASSWORD="qwerty",
        ).database_url_from_db_components()
    err = json.loads(exc_info.value.json())
    assert isinstance(err, list)
    assert err == [
        {
            "loc": ["schema"],
            "msg": "db user MUST be set when password is set",
            "type": "value_error",
        }
    ]


@mock.patch.dict(
    os.environ,
    {
        "DATABASE_URL": "postgresql://u:p@h:1/d",
    },
    clear=True,
)
@mock.patch.object(Settings.Config, "env_file", None)
@mock.patch.object(Settings.Config, "secrets_dir", None)
def test_db_components_from_database_url() -> None:
    settings = Settings().db_components_from_database_url()

    assert settings.DB_DRIVER == "postgresql"
    assert settings.DB_HOST == "h"
    assert settings.DB_NAME == "d"
    assert settings.DB_PASSWORD == "p"  # noqa: S105
    assert settings.DB_PORT == 1
    assert settings.DB_USER == "u"


@mock.patch.dict(
    os.environ,
    {
        "DATABASE_URL": "postgresql://u:p@h:1/d",
    },
    clear=True,
)
@mock.patch.object(Settings.Config, "env_file", None)
@mock.patch.object(Settings.Config, "secrets_dir", None)
def test_issue_51_db_url_integer_port() -> None:
    settings = Settings().db_components_from_database_url()
    assert settings.DB_PORT == 1
    url = settings.database_url_from_db_components()
    assert url == "postgresql://u:p@h:1/d"

    settings.DB_PORT = 5432
    assert settings.DB_PORT == 5432
    url = settings.database_url_from_db_components()
    assert url == "postgresql://u:p@h:5432/d"
