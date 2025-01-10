import json

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from news_scrapper.parsers.india_today_parser import IndiaTodayParser


class CrimeNewsSpider(CrawlSpider):
    name = "news_spider"
    allowed_domains = ["indiatoday.in"]
    start_urls = ["https://www.indiatoday.in/crime"]

    # Follow links from each response extracted from indiatoday.in/crime page
    # Fetch unique results only hence unique=True 
    rules = (Rule(LinkExtractor(allow=(r"https://www\.indiatoday\.in/crime(/.*)?$"),
                                unique=True,),
                                follow=True),
    )

    def parse_start_url(self, response):
        domain = response.url.split("//")[1].split(".")[1]
        if "indiatoday" in domain:
            india_today = IndiaTodayParser()
            yield from india_today.parse_front_page(response)
    
