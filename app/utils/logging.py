import logging
from colorlog import ColoredFormatter


def set_logging():
    # Set color formatter
    formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%y-%m-%d %H:%M:%S",
        reset=True,
        style="%",
    )
    # Set console handler
    ch = logging.StreamHandler()

    # Set formatter to console handler
    ch.setFormatter(formatter)

    # Add console handler to root logger (which is the parent of all loggers)
    logging.getLogger().addHandler(ch)

    # Set root logger level
    logging.getLogger().setLevel(logging.INFO)
