import logging
import sys


def set_up_logging(logger: logging.Logger, log_level = "INFO", file_name = sys.stdout):
    log_handler = logging.FileHandler(filename=file_name)
    formatter = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_handler.setFormatter(formatter)
    logger.setLevel(logging.getLevelName(log_level.upper()))
    logger.addHandler(log_handler)

