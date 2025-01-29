# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

"""
This module provides a model or a template for the scraped items

How To Use This Module
======================

For example:
1. Import class :py:class:`NewsScrapperItem`:
   ``from news_scrapper.items import NewsScrapperItem``.

2. Import `ItemField` enum as:
   ``from news_scrapper.const import ItemField``

2. Instantiate the class as::
   news_item = NewsScrapperItem()

3. Update the `news_item` dict with required fields:
   news_item[ItemField.SOURCE.value] = <value>
"""

import scrapy


class NewsScrapperItem(scrapy.Item):
    """
    Initializes a :py:class:`NewsScrapperItem` object.
    Defines the model for scraped items that can be returned.

    ::return: a new :py:class:`NewsScrapperItem` object
    """

    # define the fields for your item here like:
    # name = scrapy.Field()
    source = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()
    location = scrapy.Field()
    date = scrapy.Field()
