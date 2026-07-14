"""Lightweight logging setup used across the app.

A rotating file handler plus a stream handler, configured once at startup.
"""
from __future__ import annotations

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional

from .constants import LOG_FILENAME

_LOGGER_NAME = "akena_todo"
_CONFIGURED = False


def configure_logging(log_dir: str | os.PathLike[str], level: int = logging.INFO) -> None:
    """Initialize the root logger for the app. Idempotent."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    log_path = Path(log_dir) / LOG_FILENAME
    log_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.handlers.RotatingFileHandler(
        log_path, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False
    _CONFIGURED = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a child logger under the app's root logger."""
    if name is None:
        return logging.getLogger(_LOGGER_NAME)
    if not name.startswith(_LOGGER_NAME):
        name = f"{_LOGGER_NAME}.{name}"
    return logging.getLogger(name)
