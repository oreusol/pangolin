import logging

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from news_scrapper.parsers.india_today_parser import IndiaTodayParser
from news_scrapper.parsers.indian_express_parser import IndianExpressParser
from config import load_config


class CrimeNewsSpider(CrawlSpider):
    CONFIG_PATH = "/home/madhura/projects/pangolin/crime_news_scrapper/config.yaml"
    name = "news_spider"

    def __init__(self):
        super().__init__()
        self.india_today = IndiaTodayParser()
        self.indian_express = IndianExpressParser()
        self.rules_list = []
        # allow localhost in order to serve request for splash server running on localhost
        self.allowed_domains = ["localhost"]
        config = load_config(file_path=self.CONFIG_PATH)
        self.config = config.get("spider", {})
        for domain, domain_config in self.config.items():
            self.allowed_domains.append(domain)
            self.start_urls.append(domain_config.get("start_url", ""))
            self.rules_list.append(Rule(LinkExtractor(allow=(domain_config.get("allow", "")),
                                                    unique=domain_config.get("unique", True,)),
                                                    follow=domain_config.get("follow", True),),)
        self.rules = tuple(self.rules_list)


    def parse_start_url(self, response):
        domain = response.url.split("//")[1].split(".")[1]
        if "indiatoday" in domain:
            IndiaTodayParser.CLICKS += 1
            yield from self.india_today.parse_front_page(response)
        if "indianexpress" in response.url:
            IndianExpressParser.CLICKS += 1
            yield from self.indian_express.parse_front_page(response)
    
    def closed(self, reason):
        self.indian_express.logger.info(f"Total web page clicks: {IndianExpressParser.CLICKS}")
        self.india_today.logger.info(f"Total Load more clicks: {IndiaTodayParser.LOAD_MORE_CLICKS}")
        self.india_today.logger.info(f"Total web page clicks: {IndiaTodayParser.CLICKS}")