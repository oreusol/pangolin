import json

import scrapy
from scrapy.spiders import CrawlSpider


class CrimeNewsSpider(CrawlSpider):
    name = "news_spider"

