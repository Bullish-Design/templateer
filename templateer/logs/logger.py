import os
import logging
from logging.handlers import RotatingFileHandler

# Import logdir:
from miragram.src.base.config import logdir


# get_logger function
def get_logger(name, stream=False):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create logs directory if it doesn't exist
    if not os.path.exists(logdir):
        os.makedirs(logdir)

    # Create file handler
    file_handler = RotatingFileHandler(
        f"{logdir}/{name}.log",
        maxBytes=1024 * 1024 * 10,  # 10MB
        backupCount=5,
    )
    file_handler.setLevel(logging.DEBUG)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create console handler
    if stream:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    file_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)

    for i in range(2):
        logger.info("")
    logger.info(
        f"\n\n\n\n\n**************** {name} Logger initialized ****************\n\n\n\n"
    )
    logger.info("")
    return logger
