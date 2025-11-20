"""Centralized logging configuration utilities."""
from __future__ import annotations

import logging
import os
from typing import Optional

LOG_FORMAT = "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"


def setup_logging(level: Optional[str] = None) -> None:
    """Initialize root logging with a consistent format.

    Args:
        level: Optional string log level override; falls back to the
            ``DSPM_LOG_LEVEL`` environment variable or ``INFO``.
    """

    log_level = (level or os.getenv("DSPM_LOG_LEVEL", "INFO")).upper()
    logging.basicConfig(level=log_level, format=LOG_FORMAT)


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger, ensuring logging is configured."""

    if not logging.getLogger().handlers:
        setup_logging()
    return logging.getLogger(name)
