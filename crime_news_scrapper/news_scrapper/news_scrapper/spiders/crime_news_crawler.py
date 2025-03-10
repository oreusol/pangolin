"""
Spider class defines how a certain site (or a group of sites) will be scraped,
including how to perform the crawl (i.e. follow links).

How To Use This Module
======================

This class will be actually called/instantiated by scrapy framework. For that, the custom
class must be derived from one of the scrapy spider classes. Ex here is CrawlSpider.

Following things are important to crawl multiple websites simultaneously.

1. Derive the class from :py:class:`CrawlSpider`

2. URLs to be scrapped must be part of `start_urls` list which is scrapy spider's attribute

3. To avoid middleware offset issue, add the domain in `allowed_domains` list which
   is scrapy spider's attribute

4. Create rules for what and how URLs should be scrapped
"""

import logging
import importlib
from typing import Any, Union, Iterable

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Request
from scrapy.item import Item

from config import load_config, get_config_path
from ..const import ParserType, ClassMapping
from ..log import set_up_logging


class CrimeNewsSpider(CrawlSpider):
    """
    Initializes a :py:class:`CrimeNewsSpider` object.
    Defines a custom behaviour for scraping different crime websites parallely
    with the help of in built scrapy spiders

    ::return: a new :py:class:`CrimeNewsSpider` object
    """

    name = "news_spider"

    def __init__(self):
        """
        Reads the config and initializes different rules for scrapping
        multiple websites.
        """
        super().__init__()
        self.log = logging.getLogger()
        self.rules_list = []
        # allow localhost in order to serve request for splash server running on localhost
        self.allowed_domains = ["localhost"]
        config_path = get_config_path()
        config = load_config(config_path=config_path)
        self.config = config.get("spider", {})
        self.sites = self.config.get("sites_to_crawl", [])
        if not self.sites:
            raise ValueError(
                "No any sites to crawl, there should be at least one site to start a crawl"
            )
        log_level = self.config.get("log_level", "INFO")
        log_path = self.config.get(
            "file_name",
            "crime_news_crawler.log",
        )
        set_up_logging(logger=self.log, log_level=log_level, file_name=log_path)
        del self.config["log_level"]
        del self.config["file_name"]
        del self.config["sites_to_crawl"]
        for domain, domain_config in self.config.items():
            self.allowed_domains.append(domain)
            # A list of URLs where the spider will begin to crawl from
            self.start_urls.append(domain_config.get("start_url", ""))
            # Rules for crawling websites(how they can be crawled)
            # Allow only specific given URL. Avoid duplication and follow
            # the subequent URLs from that URL.
            self.rules_list.append(
                Rule(
                    LinkExtractor(
                        allow=(domain_config.get("allow", "")),
                        unique=domain_config.get(
                            "unique",
                            True,
                        ),
                    ),
                    follow=domain_config.get("follow", True),
                ),
            )
        self.rules = tuple(self.rules_list)
        self.log.info("Initiating crawl for %s", self.start_urls)

    def get_parser(self, site: str) -> Any:
        """
        Dynamically imports the parser class and returns its instance
        """
        try:
            self.log.info("Initializing the parser for %s:", site)
            parser_type = ClassMapping[ParserType[site.upper()].value].value
            module_path, class_name = parser_type.rsplit(".", 1)
            self.log.info("Importing the module %s:", class_name)
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            return cls()
        except ImportError as i_err:
            raise ImportError(f"Unable to import module for {site}: {i_err}") from i_err
        except Exception as err:
            raise Exception(f"Instantiation failed for a parser: {site}: {err}") from err

    def parse_start_url(
        self, response, **kwargs
    ) -> Union[Request, Item, Iterable[Union[Request, Item]]]:
        """
        This method is called for each response produced for the URLs in
        the spider's ``start_urls`` attribute. It allows to parse
        the initial responses and must return either an
        :ref:`item object`, py:class:`scrapy.Request`
        object, or an iterable containing any of them.
        :param response: py:class:`scrapy.http.response.TextResponse` object
        ::return: `scrapy.http.Request` or `scrapy.Item` object or its iterable
        """
        domain = response.url.split("//")[1].split(".")[1]
        if ParserType.INDIATODAY.name.lower() in domain:
            if ParserType.INDIATODAY.name.lower() in self.sites:
                self.india_today = self.get_parser(site=ParserType.INDIATODAY.name)
                self.india_today.CLICKS += 1
                self.log.info("Started crawling front page for %s", response.url)
                yield from self.india_today.parse_front_page(response=response)
        if ParserType.INDIANEXPRESS.name.lower() in response.url:
            if ParserType.INDIANEXPRESS.name.lower() in self.sites:
                self.indian_express = self.get_parser(site=ParserType.INDIANEXPRESS.name)
                self.indian_express.CLICKS += 1
                self.log.info("Started crawling front page for %s", response.url)
                yield from self.indian_express.parse_front_page(response=response)

    def closed(self, reason) -> None:
        """
        Called when the spider closes. This method provides a shortcut to
        signals.connect() for the spider_closed signal.
        :param reason: a string describing the spider closure reason
        """
        self.log.info("Closing the spider with reason as: %s", reason)
        self.indian_express.logger.info(f"Total web page clicks: {self.indian_express.CLICKS}")
        self.india_today.logger.info(f"Total Load more clicks: {self.india_today.LOAD_MORE_CLICKS}")
        self.india_today.logger.info(f"Total web page clicks: {self.india_today.CLICKS}")
