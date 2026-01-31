from __future__ import annotations
from loguru import logger
import sys

def configure_logging():
    logger.remove()
    logger.add(sys.stdout, level="INFO", enqueue=True, backtrace=False, diagnose=False)
    return logger
