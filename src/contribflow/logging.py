from __future__ import annotations

import sys

from loguru import logger


def configure_logging():
    logger.remove()
    logger.add(sys.stdout, level="INFO", enqueue=True, backtrace=False, diagnose=False)
    return logger
