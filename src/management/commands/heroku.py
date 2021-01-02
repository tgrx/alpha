import json

import requests

from framework.config import settings
from management.commands.abstract import ManagementCommand

assert settings.HEROKU_APP_NAME, "Heroku app name is not configured"

HEROKU_API_URL = f"https://api.heroku.com/apps/{settings.HEROKU_APP_NAME}"


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
        app_name = settings.HEROKU_APP_NAME
        assert app_name, "unable to get info about Heroku app: name is not set"

        token = settings.HEROKU_API_TOKEN
        assert (
            token
        ), "Heroku API token is not set: see https://help.heroku.com/PBGP6IDE/"

        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        response = requests.get(HEROKU_API_URL, headers=headers)
        if response.status_code == 403:
            raise AssertionError(f"invalid Heroku API token: {response.json()}")

        assert (
            response.status_code == 200
        ), f"unable to get app info: {response.status_code}\n{response.content}"

        payload = response.json()
        print(json.dumps(payload, sort_keys=True, indent=4))

    @staticmethod
    def _configure():
        token = settings.HEROKU_API_TOKEN

        url = f"{HEROKU_API_URL}/config-vars"

        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = {
            "ALPHA_ENV": "heroku",
            "PYTHONPATH": "src",
            "SENTRY_DSN": settings.SENTRY_DSN,
        }

        resp = requests.patch(url, headers=headers, json=payload)
        assert (
            resp.status_code == 200
        ), f"unable to get app info: {resp.status_code}\n{resp.content}"

        payload = resp.json()
        print(json.dumps(payload, sort_keys=True, indent=4))
