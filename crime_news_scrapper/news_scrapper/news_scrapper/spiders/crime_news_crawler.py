from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from news_scrapper.parsers.india_today_parser import IndiaTodayParser
from news_scrapper.parsers.indian_express_parser import IndianExpressParser


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

    def __init__(self):
        super().__init__()
        self.india_today = IndiaTodayParser()
        self.indian_express = IndianExpressParser()


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