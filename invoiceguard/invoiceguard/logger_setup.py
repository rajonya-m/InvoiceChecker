"""Logging to both the screen and a file (CONCEPT: logging module)."""
import logging
import os

from invoiceguard.config import LOG_FILE


def get_logger(name="invoiceguard"):
    logger = logging.getLogger(name)
    if logger.handlers:                # already set up, don't add twice
        return logger

    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s")

    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(fmt)
    console = logging.StreamHandler()
    console.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console)
    return logger
