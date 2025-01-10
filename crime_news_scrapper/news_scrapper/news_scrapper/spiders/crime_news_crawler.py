import json

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from news_scrapper.parsers.india_today_parser import IndiaTodayParser


class CrimeNewsSpider(CrawlSpider):
    name = "news_spider"

    # allow localhost in order to serve request for splash server running on localhost
    allowed_domains = ["indiatoday.in", "indianexpress.com", "localhost"]
    start_urls = ["https://www.indiatoday.in/crime", "https://www.indianexpress.com/about/crime-news"]

    # Follow links from each response extracted from indiatoday.in/crime page and
    # indianexpress.com/about/crime-news page
    # Fetch unique results only hence unique=True 
    rules = (Rule(
                    LinkExtractor(allow=(r"https://www\.indiatoday\.in/crime(/.*)?$"),
                                unique=True,),
                                follow=True),
             Rule(
                    LinkExtractor(allow=(r"https://www\.indianexpress\.com/about/crime-news/"),
                                   unique=False,),
                                   follow=True),

    )

    def parse_start_url(self, response):
        domain = response.url.split("//")[1].split(".")[1]
        if "indiatoday" in domain:
            india_today = IndiaTodayParser()
            yield from india_today.parse_front_page(response)
        if "indianexpress" in response.url:
            indian_express = IndianExpressParser()
            yield from indian_express.parse_front_page(response)

    
