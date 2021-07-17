import logging

from framework.config import settings

FORMATS = {
    False: "{asctime} | {name}.{levelname} | {module}.{funcName} | {message}",
    True: "{asctime} | {name}.{levelname}\n| {pathname}:{lineno}\n| {message}\n",
}

LEVELS = {
    False: logging.INFO,
    True: logging.DEBUG,
}


def get_logger(logger_name: str) -> logging.Logger:
    debug = settings.MODE_DEBUG

    lvl = LEVELS[debug]
    fmt = FORMATS[debug]

    logger = logging.getLogger(logger_name)
    logger.setLevel(lvl)

    handler = logging.StreamHandler()
    handler.setLevel(lvl)

    formatter = logging.Formatter(
        fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S", style="{"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def mute_root_logger() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.CRITICAL)
    for _handler in root_logger.handlers:
        root_logger.removeHandler(_handler)


mute_root_logger()
