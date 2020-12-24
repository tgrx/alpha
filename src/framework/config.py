import os
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
    return convert(value)


DATABASE_URL = get_setting("DATABASE_URL")
HEROKU_API_APP_ID = get_setting("HEROKU_API_APP_ID")
HEROKU_API_TOKEN = get_setting("HEROKU_API_TOKEN")
HOST = get_setting("HOST")
MODE_DEBUG = get_setting("MODE_DEBUG", True, convert=bool)
PORT = get_setting("PORT", 8000, convert=int)
REQUEST_TTL = get_setting("REQUEST_TTL", convert=int)
SENTRY_DSN = get_setting("SENTRY_DSN")
TEST_BROWSER = get_setting("TEST_BROWSER")
TEST_BROWSER_HEADLESS = get_setting("TEST_BROWSER_HEADLESS", True, convert=bool)
VENV_SYNTHETIC = get_setting("VENV_SYNTHETIC", False, convert=bool)
WEB_CONCURRENCY = get_setting("WEB_CONCURRENCY", cpu_count() * 2 + 1, convert=int)
