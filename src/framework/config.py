import os
import sys
from multiprocessing import cpu_count


def get_setting(setting_name, default=None, convert=lambda _value: _value or None):
    """
    Returns a setting value: either from ENV var or from Dynaconf.
    If none found, default is used.
    If convert is provided, it converts a value of setting.

    :param setting_name: setting name
    :param default: default value if nothing is found
    :param convert: a converter for a found value
    :return: a value
    """

    value = os.getenv(setting_name)
    if not value:
        try:
            from dynaconf import settings

            value = settings.get(setting_name)
        except ImportError:
            pass

    value = value if value is not None else default
    try:
        value = convert(value)
    except Exception:
        msg = (
            f"CONFIG ERROR:"
            f" cannot convert {setting_name}={value!r}"
            f" with {convert.__name__},"
            f" using None"
        )
        value = None
        print(msg, file=sys.stderr)

    return value


DATABASE_URL = get_setting("DATABASE_URL")
HEROKU_API_APP_ID = get_setting("HEROKU_API_APP_ID")
HEROKU_API_TOKEN = get_setting("HEROKU_API_TOKEN")
HEROKU_APP_NAME = get_setting("HEROKU_APP_NAME")
HOST = get_setting("HOST")
MODE_DEBUG = get_setting("MODE_DEBUG", True, convert=bool)
PORT = get_setting("PORT", 8000, convert=int)
REQUEST_TIMEOUT = get_setting("REQUEST_TIMEOUT", convert=int)
SENTRY_DSN = get_setting("SENTRY_DSN")
TEST_BROWSER = get_setting("TEST_BROWSER")
TEST_BROWSER_HEADLESS = get_setting("TEST_BROWSER_HEADLESS", True, convert=bool)
VENV_SYNTHETIC = get_setting("VENV_SYNTHETIC", False, convert=bool)
WEB_CONCURRENCY = get_setting("WEB_CONCURRENCY", cpu_count() * 2 + 1, convert=int)
