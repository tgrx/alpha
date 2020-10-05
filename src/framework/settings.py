import os

from dynaconf import settings as _ds

PORT = int(os.getenv("PORT", _ds.get("PORT", 8000)))
