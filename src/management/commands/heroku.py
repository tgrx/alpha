import json
from typing import Dict
from typing import Optional

import requests
from requests import Response

from framework.config import settings
from management.commands.abstract import ManagementCommand

HEROKU_API_URL = "https://api.heroku.com/apps"


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        assert settings.HEROKU_APP_NAME, "Heroku app name is not configured"
        assert (
            settings.HEROKU_API_TOKEN
        ), "Heroku API token is not set: see https://help.heroku.com/PBGP6IDE/"

    def __call__(self):
        if self.option_is_active("--configure"):
            self._configure()
        else:
            self._get_config()

    @classmethod
    def _get_config(cls):
        response = cls._api_call()
        payload = response.json()
        print(json.dumps(payload, sort_keys=True, indent=4))

    @classmethod
    def _configure(cls):
        payload = {
            "ALPHA_ENV": "heroku",
            "PYTHONPATH": "src",
            "SENTRY_DSN": settings.SENTRY_DSN,
        }

        response = cls._api_call(
            method="patch", path="config-vars", payload=payload
        )
        payload = response.json()
        print(json.dumps(payload, sort_keys=True, indent=4))

    @staticmethod
    def _api_call(
        *,
        method: str = "get",
        path: str = "",
        payload: Optional[Dict] = None,
    ) -> Response:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {settings.HEROKU_API_TOKEN}",
            "Content-Type": "application/json",
        }

        url = f"{HEROKU_API_URL}/{settings.HEROKU_APP_NAME}/{path}"

        meth = getattr(requests, method.lower())

        meth_kwargs = {
            "headers": headers,
        }
        if payload:
            meth_kwargs["json"] = payload

        response = meth(url, **meth_kwargs)
        assert (
            response.status_code == 200
        ), f"unable to get app info: {response.status_code}\n{response.content}"

        return response
