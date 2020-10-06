import os
import sys
from urllib.parse import urlsplit


def get_setting(setting_name, default=None, *, convert=lambda _value: _value or None):
    value = os.getenv(setting_name)
    if not value:
        try:
            from dynaconf import settings

            value = settings.get(setting_name)
        except ImportError:
            pass

    value = value or default
    return convert(value)


def in_virtualenv():
    synth_venv = get_setting("VENV_SYNTHETIC", False, convert=bool)
    actual_venv = _discover_venv_by_prefix()
    return synth_venv or actual_venv


def get_db_name():
    url = get_setting("DATABASE_URL")
    if not url:
        return "--- no database configured ---"

    url = urlsplit(url)
    name = url.path.replace("/", "")
    return name


def get_db_username():
    url = get_setting("DATABASE_URL")
    if not url:
        return "--- no database configured ---"

    url = urlsplit(url)
    return url.username


def _discover_venv_by_prefix():
    compat_prefix = _get_base_prefix_compat()
    return compat_prefix != sys.prefix


def _get_base_prefix_compat():
    prefix = (
        getattr(sys, "base_prefix", None)
        or getattr(sys, "real_prefix", None)
        or sys.prefix
    )

    return prefix
