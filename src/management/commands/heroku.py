import json

import requests

from framework import config
from management.commands.abstract import ManagementCommand

HEROKU_APPS_API = "https://api.heroku.com/apps"


class HerokuCommand(ManagementCommand):
    name = "heroku"
    help = (
        "Heroku management command."
        " If called without arguments, prints an app config in JSON format."
        " Both HEROKU_APP_NAME and HEROKU_API_KEY MUST be configured."
    )
    arguments = {
        "--configure": (
            "Configures your app on Heroku."
            " Both HEROKU_APP_NAME and HEROKU_API_KEY MUST be configured."
        ),
    }

    def __call__(self):
        if self.option_is_active("--configure"):
            self._configure()
        else:
            self._get_config()

    @staticmethod
    def _get_config():
        app_name = config.HEROKU_APP_NAME
        assert app_name, "unable to get info about Heroku app: name is not set"

        token = config.HEROKU_API_TOKEN
        assert (
            token
        ), "Heroku API token is not set: see https://help.heroku.com/PBGP6IDE/"

        url = f"{HEROKU_APPS_API}/{app_name}"
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 403:
            raise AssertionError(f"invalid Heroku API token: {response.json()}")

        assert (
            response.status_code == 200
        ), f"unable to get app info: {response.status_code}\n{response.content}"

        payload = response.json()
        print(json.dumps(payload, sort_keys=True, indent=4))

    @staticmethod
    def _configure():
        token = config.HEROKU_API_TOKEN
        app_id = config.HEROKU_API_APP_ID
        sentry_dsn = config.SENTRY_DSN

        url = f"{HEROKU_APPS_API}/{app_id}/config-vars"

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
        assert (
            resp.status_code == 200
        ), f"unable to get app info: {resp.status_code}\n{resp.content}"

        payload = resp.json()
        print(json.dumps(payload, sort_keys=True, indent=4))
