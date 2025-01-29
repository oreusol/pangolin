"""
This module provides application logging functionality, its setup and configuration
"""

import logging
import sys

from pythonjsonlogger.json import JsonFormatter


def set_up_logging(logger: logging.Logger, log_level="INFO", file_name=sys.stdout):
    """
    Creates and configures proper JSON logging

    :param logger: The py:class:`logging.Logger` object.
    :param log_level: log level to set.
    :param file_name: File path to dump all the logs.
    """
    log_handler = logging.FileHandler(filename=file_name)
    formatter = JsonFormatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_handler.setFormatter(formatter)
    logger.setLevel(logging.getLevelName(log_level.upper()))
    logger.addHandler(log_handler)
