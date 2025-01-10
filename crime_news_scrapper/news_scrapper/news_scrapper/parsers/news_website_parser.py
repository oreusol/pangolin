import logging
from typing import Optional

from news_scrapper.log import set_up_logging


class NewsWebsiteParser:

    def __init__(self,
                 logger: Optional[logging.getLogger] = None,
                 log_level: str = "INFO",
                 file_name: str = "/home/madhura/projects/pangolin/crime_news_scrapper/news_scrapper.log"):
        self.source = ""
        self.logger = logger or logging.getLogger(name="crime_scrapper")
        if logger is None:
            set_up_logging(logger=self.logger, log_level=log_level, file_name=file_name)

    def parse_front_page(self):
        raise NotImplementedError()
