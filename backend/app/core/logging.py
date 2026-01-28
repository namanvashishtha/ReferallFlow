import sys
from loguru import logger
from .config import settings

# Basic loguru configuration for structured logs
logger.remove()
logger.add(sys.stdout, level=settings.LOG_LEVEL, colorize=True, backtrace=True, diagnose=False)

# Helper to get module-level logger
def get_logger(name: str = "app"):
    return logger.bind(module=name)
