from urllib.parse import urlsplit

from framework import config


def get_db_host():
    url = config.DATABASE_URL
    if not url:
        return "--- no database configured ---"

    url = urlsplit(url)
    host = url.hostname
    return host


def get_db_port():
    url = config.DATABASE_URL
    if not url:
        return "--- no database configured ---"

    url = urlsplit(url)
    port = int(url.port or 5432)
    return port


def get_db_name():
    url = config.DATABASE_URL
    if not url:
        return "--- no database configured ---"

    url = urlsplit(url)
    name = url.path.replace("/", "")
    return name


def get_db_username():
    url = config.DATABASE_URL
    if not url:
        return "--- no database configured ---"

    url = urlsplit(url)
    return url.username
