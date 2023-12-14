import logging
from colorlog import ColoredFormatter


def set_logging():
    # Set color formatter
    log_format = "%(log_color)s%(asctime)s [%(name)s] %(levelname)s: %(message)s"
    formatter = ColoredFormatter(
        log_format,
        datefmt="%y-%m-%d %H:%M:%S",
        reset=True,
        style="%",
    )
    logger = logging.getLogger()

    # Clear existing handlers to avoid duplicate logs if set_logging is called multiple times
    logger.handlers = []

    # Set console handler
    ch = logging.StreamHandler()

    # Set formatter to console handler
    ch.setFormatter(formatter)

    # Add console handler to root logger (which is the parent of all loggers)
    logger.addHandler(ch)

    # Set root logger level
    logger.setLevel(logging.INFO)
