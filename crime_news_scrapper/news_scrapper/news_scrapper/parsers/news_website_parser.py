"""
This module defines base implementation for any parser that will parse
different crime websites.
"""

import logging
from typing import Optional

from scrapy.http import TextResponse
from ..log import set_up_logging


class NewsWebsiteParser:
    """
    Module represents the base design template for any parsers.
    """

    def __init__(
        self,
        logger: Optional[logging.getLogger] = None,
        log_level: str = "INFO",
        file_name: str = "news_scrapper.log",
    ):
        """
        Performs basic functionality for parser initialization.
        :param logger: `loggging.getLogger` object
        :param log level: log level to set for a parser
        :param file_name: file path to log
        """
        self.source = ""
        self.logger = logger or logging.getLogger(name=self.__class__.__name__)
        if logger is None:
            set_up_logging(logger=self.logger, log_level=log_level, file_name=file_name)

    def parse_front_page(self, response: TextResponse):
        """
        Abstract method to parse front page of any crime website
        :param response: An instance of `scrapy.http.response.TextResponse`
        """
        raise NotImplementedError()
