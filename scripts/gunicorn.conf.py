from multiprocessing import cpu_count

try:
    from pathlib import Path

    _this_dir = Path(__file__).parent.resolve().as_posix()
    import sys

    sys.path.append(_this_dir)

    from consts import DIR_SRC
    from utils import get_setting
finally:
    print("[done] reading Gunicorn config")

# --------------------------------------------

_port = get_setting("PORT", 8000, convert=int)
bind = f"0.0.0.0:{_port}"
chdir = DIR_SRC.as_posix()
graceful_timeout = 10
max_requests = 200
max_requests_jitter = 20
pythonpath = DIR_SRC.as_posix()
reload = False
timeout = 30
workers = get_setting("WEB_CONCURRENCY", cpu_count() * 2 + 1, convert=int)
