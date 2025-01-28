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
