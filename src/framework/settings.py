import os

from dynaconf import settings as _ds

HOST = "localhost"
PORT = int(os.getenv("PORT", _ds.get("PORT", 8000)))
