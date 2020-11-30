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
