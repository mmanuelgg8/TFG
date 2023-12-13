import logging
from colorlog import ColoredFormatter


def setup_logger(class_name: str = "app") -> logging.Logger:
    # Create a logger
    logger = logging.getLogger(class_name)
    logger.setLevel(logging.INFO)

    # Create a console handler and set the formatter
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Create a color formatter with default colors
    formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s %(levelname)s:%(name)s:%(message)s",
        datefmt=None,
        reset=True,
        style="%",
    )

    # Add the formatter to the handler
    ch.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(ch)

    return logger
