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

from datetime import datetime
import re
from typing import Union

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst


def clean_whitespace(value: str) -> str:
    """
    A helper function which removes whitespace from
    a given string.
    :param value: string to be cleaned.
    ::return: A clean string without whitespace.
    """
    return value.strip()


def convert_date(date: Union[list, str]) -> datetime:
    """
    Extract data from the given input and convert it
    to a required strctured format
    :param date: Either a list or a string date to be processed
    :return: a `datetime.datetime` object
    """
    formats = [
        "%b %d, %Y %I:%M %p",
        "%B %d, %Y %I:%M %p",
        "%b %d, %Y %H:%M",
        "%B %d, %Y %H:%M",
        "%b %d, %Y %H:%M IST",
        "%B %d, %Y %H:%M IST",
    ]
    for fmt in formats:
        try:
            dt_obj = datetime.strptime(date, fmt)
            return dt_obj.strftime("%d-%m-%y %H-%M-%S")
        except ValueError:
            continue
    raise ValueError(f"Unknown date format: {date}")


def remove_escape_characters(text: str) -> str:
    """
    Removes escape sequences from a given string.
    :param text: A string to be processed.
    ::return: A clean string without escape sequnces.
    """
    clean_text = re.sub(r"[\a\b\f\n\r\t\v]", "", text)
    return clean_text


class NewsScrapperItem(scrapy.Item):
    """
    Initializes a :py:class:`NewsScrapperItem` object.
    Defines the model for scraped items that can be returned.
    ::return: a new :py:class:`NewsScrapperItem` object
    """

    # define the fields for your item here like:
    source = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(
        input_processor=MapCompose(remove_escape_characters, clean_whitespace),
        output_processor=TakeFirst(),
    )
    url = scrapy.Field(output_processor=TakeFirst())
    description = scrapy.Field(
        input_processor=MapCompose(remove_escape_characters, clean_whitespace),
        output_processor=TakeFirst(),
    )
    location = scrapy.Field(
        input_processor=MapCompose(clean_whitespace), output_processor=TakeFirst()
    )
    date = scrapy.Field(
        input_processor=MapCompose(convert_date, clean_whitespace),
        output_processor=TakeFirst(),
    )
