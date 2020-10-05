import multiprocessing
from os import getenv
from pathlib import Path

from dynaconf import settings

DIR_SCRIPTS = Path(__file__).parent.resolve()
DIR_REPO = DIR_SCRIPTS.parent.resolve()
DIR_SRC = (DIR_REPO / "src").resolve()

RELOAD = True
NR_WORKERS = multiprocessing.cpu_count() * 2 + 1  # XXX hahaha classic

PORT = getenv("PORT", settings.get("PORT", 8000))
assert PORT and PORT.isdecimal(), f"invalid port: `{PORT!r}`"
PORT = int(PORT)

if "heroku" in settings.ENV_FOR_DYNACONF:
    RELOAD = False

    NR_WORKERS = getenv("WEB_CONCURRENCY", "2")
    assert NR_WORKERS and NR_WORKERS.isdecimal(), f"invalid workers nr: `{PORT!r}`"
    NR_WORKERS = int(NR_WORKERS)

bind = f"0.0.0.0:{PORT}"
chdir = DIR_SRC.as_posix()
graceful_timeout = 10
max_requests = 200
max_requests_jitter = 20
pythonpath = DIR_SRC.as_posix()
reload = RELOAD
timeout = 30
workers = NR_WORKERS
