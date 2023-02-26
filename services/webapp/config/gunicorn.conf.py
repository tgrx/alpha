from alpha.dirs import DIR_APP
from alpha.settings import Settings

settings = Settings()

bind = f"0.0.0.0:{settings.PORT}"
chdir = DIR_APP.as_posix()
graceful_timeout = settings.REQUEST_TIMEOUT
max_requests = 200
max_requests_jitter = 20
pythonpath = DIR_APP.as_posix()
reload = False
timeout = graceful_timeout * 2
worker_class = "uvicorn.workers.UvicornH11Worker"
workers = settings.WEB_CONCURRENCY
