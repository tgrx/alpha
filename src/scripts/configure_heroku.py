import requests

from framework.util.settings import get_setting

API = "https://api.heroku.com/apps"


def set_config_vars():
    token = get_setting("HEROKU_API_TOKEN")
    app_id = get_setting("HEROKU_API_APP_ID")
    sentry_dsn = get_setting("SENTRY_DSN")

    url = f"{API}/{app_id}/config-vars"

    headers = {
        "Accept": "application/vnd.heroku+json; version=3",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "DYNACONF_SENTRY_DSN": sentry_dsn,
        "ENV_FOR_DYNACONF": "heroku",
        "PYTHONPATH": "src",
    }

    resp = requests.patch(url, headers=headers, json=payload)
    print(resp.json())


if __name__ == "__main__":
    set_config_vars()
