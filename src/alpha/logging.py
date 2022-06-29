import logging

import structlog

from alpha.settings import Settings

settings = Settings()

level = {
    True: logging.DEBUG,
    False: logging.INFO,
}[settings.MODE_DEBUG]

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(level),
)

logger = structlog.get_logger()
