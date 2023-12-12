import logging
from colorlog import ColoredFormatter


def setup_logger():
    # Create a logger
    logger = logging.getLogger("example_logger")
    logger.setLevel(logging.DEBUG)

    # Create a console handler and set the formatter
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create a color formatter with default colors
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)s:%(name)s:%(message)s",
        datefmt=None,
        reset=True,
        style="%",
    )

    # Add the formatter to the handler
    ch.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(ch)

    return logger
