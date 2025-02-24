"""
A module that stores any static variables, used as constants throughout Crime News Scrapper

How To Use This Module
======================

For example:
1. Import class :py:class:`ItemField`:
   ``from news_scrapper.const import ItemField``.

2. Use the constants and its values as::
   ItemField.TITLE.value

"""

from enum import Enum


class ItemField(Enum):
    """
    An enumeration that provides constants (keys)
    for items to be returned as a scrapy response
    """

    SOURCE = "source"
    TITLE = "title"
    DESCRIPTION = "description"
    URL = "url"
    LOCATION = "location"
    DATE = "date"


class ParserType(Enum):
    """Enum for different parser types"""

    INDIATODAY = "INDIATODAYPARSER"
    INDIANEXPRESS = "INDIANEXPRESSPARSER"


class ClassMapping(Enum):
    """Enum for class to its module mapping"""

    INDIATODAYPARSER = "news_scrapper.parsers.india_today_parser.IndiaTodayParser"
    INDIANEXPRESSPARSER = "news_scrapper.parsers.indian_express_parser.IndianExpressParser"
