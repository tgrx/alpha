from urllib.parse import urlsplit


def get_settings():
    settings = None
    try:
        from dynaconf import settings as _settings

        settings = _settings
    except ImportError:
        pass

    return settings


def get_db_name():
    name = "--- no database configured: no Dynaconf, no settings or whatever else ---"

    settings = get_settings()
    if not settings:
        return name

    url = urlsplit(settings.DATABASE_URL)
    name = url.path.replace("/", "")
    return name


def main():
    name = get_db_name()
    print(name)


if __name__ == "__main__":
    main()
