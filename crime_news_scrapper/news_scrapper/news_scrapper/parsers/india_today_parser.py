"""
This module helps in parsing the response for `www.indiatoday.in/crime`
page. Each crime story from the response will be parsed in order to get required items
and those items will be returned one by one.

How To Use This Module
======================

1. Import class :py:class:`IndiaTodayParser`:
    from news_scrapper.parsers.india_today_parser import IndiaTodayParser

2. Instantiate the class as::
   india_today = IndiaTodayParser()

3. Start parsing by using:
   self.india_today.parse_front_page(response=response)


"""

import json
from typing import Iterable, Iterator

import scrapy
from scrapy.http import Request
from scrapy.http import TextResponse

from config import get_config_path, load_config
from ..items import NewsScrapperItem
from ..parsers.news_website_parser import NewsWebsiteParser
from ..const import ItemField


class IndiaTodayParser(NewsWebsiteParser):
    """
    Initializes a :py:class:`IndiaTodayParser` object.
    Defines parsing mechanism to parse the response received from
    `https://www.indiatoday.in/crime`.

    ::return: a new :py:class:`IndiaTodayParser` object
    """

    CLICKS = 0
    LOAD_MORE_CLICKS = 0

    def __init__(self):
        """
        Reads the config and initializes basic parsing logic
        """
        config_path = get_config_path()
        config = load_config(config_path=config_path)
        self.config = config.get("india_today_parser", {})
        logger_level = "INFO"
        logger_path = "india_today.log"
        if self.config:
            logger_level = self.config.get("log_level", "INFO")
            logger_path = self.config.get(
                "file_name",
                "india_today.log",
            )
        super().__init__(log_level=logger_level, file_name=logger_path)
        self.source = "INDIATODAY"

    def parse_front_page(self, response: TextResponse) -> Iterator[Request]:
        """
        Iterate over each story from response and extract required details using xpath
        selectors. Each story response will be modelled as an instance of `NewsScrapperItem`.
        Also, makes a scrapy request again to each specific story url to get more information.
        Additionally, this method initiates the process to load more contents using ajax calls
        to news server. This is achieved with the help of `scrapy.FormRequest`.
        :param response: An instance of `scrapy.http.TextResponse`
        :return: Yields `scrapy.Request` objects, including `scrapy.FormRequest` for AJAX calls
        """
        self.logger.info(f"Fetching the data from: {self.source.lower()}.in page")
        # This will parse the front page of indiatoday crime page. xpath selector value
        # "article" will give list of stories. Iterating those can give value for
        # story title, story url and the description by using appropriate selector.
        for crime_news in response.xpath(".//article"):
            news_item = NewsScrapperItem()
            news_item[ItemField.SOURCE.value] = self.source
            news_item[ItemField.TITLE.value] = crime_news.xpath("./div/div/a/@title").get()
            news_item[ItemField.URL.value] = crime_news.xpath("./div/div/a/@href").get()
            news_item[ItemField.DESCRIPTION.value] = crime_news.xpath(
                "./div/div/div/p/text()"
            ).get()
            if news_item[ItemField.URL.value] is not None:
                # Again make a request to a specific story in order to get the date and
                # the location associated with it. Pass already created news_item dictionary
                # as its meta field which will be passed in the next request and will be available
                # in the response so that same dictionary can be updated for location and date.
                # filter duplicate links hence dont_filter=False
                self.logger.debug(
                    f"Fetching the data from the story: {news_item[ItemField.URL.value]} page"
                )
                yield response.follow(
                    url=news_item[ItemField.URL.value],
                    callback=self.parse_story,
                    meta={"items": news_item},
                    dont_filter=False,
                )

        # Handle the "load more" contents using ajax call.
        # filter duplicate links using dont_filter=False
        self.logger.info("Loading more contents...")
        # This is the exact call which gets executed after clicking load more.
        # Executes callback self.parse_more_content after successful request execution.
        ajax_url = "https://www.indiatoday.in/api/ajax/loadmorecontent"
        page = 1
        pagepath = "/crime"
        yield scrapy.FormRequest(
            url=ajax_url,
            method="GET",
            formdata={
                "page": str(page),
                "pagepath": pagepath,
                "pagetype": "story/photo_gallery/video/breaking_news",
            },
            callback=self.parse_more_content,
            meta={"page": page, "pagepath": pagepath},
            dont_filter=False,
        )

    def parse_more_content(self, response: scrapy.FormRequest) -> Iterable[Request]:
        """
        This is a callback method for first load more execution.
        Handle the ajax response from load more request in order to get story
        title, url and description as earlier. Also, it checks if there is further
        load more available, if so, it does make new scrapy Request to load the subsequent
        contents till it reaches the last load more.
        :param response: An instance of `scrapy.FormRequest`
        :return:  Yields iterable of `scrapy.Request` objects
        """
        data = json.loads(response.text)
        new_stories = data.get("data", {}).get("content", {})
        for new_story in new_stories:
            item = NewsScrapperItem()
            item[ItemField.SOURCE.value] = self.source
            item[ItemField.TITLE.value] = new_story.get("title")
            item[ItemField.DESCRIPTION.value] = new_story.get("description_short")
            item[ItemField.URL.value] = new_story.get("canonical_url")
            if item[ItemField.URL.value] is not None:
                # Again make a request to a specific story in order to get the date and
                # the location associated with it.
                # filter duplicate links
                yield response.follow(
                    url=item[ItemField.URL.value],
                    callback=self.parse_story,
                    meta={"items": item},
                    dont_filter=False,
                )

        # Keep checking if there are contents to load and if yes, load and
        # get its data similarly. filter duplicate links
        IndiaTodayParser.LOAD_MORE_CLICKS = response.meta["page"]
        self.logger.debug(f"Loading page: {response.meta['page'] + 1}")
        if (
            data.get("data", {}).get("is_load_more", "")
            and data.get("data", {}).get("is_load_more") == 1
        ):
            ajax_url = "https://www.indiatoday.in/api/ajax/loadmorecontent"
            page = response.meta["page"] + 1
            pagepath = response.meta["pagepath"]
            yield scrapy.FormRequest(
                url=ajax_url,
                method="GET",
                formdata={
                    "page": str(page),
                    "pagepath": pagepath,
                    "pagetype": "story/photo_gallery/video/breaking_news",
                },
                callback=self.parse_more_content,
                meta={"page": page, "pagepath": pagepath},
                dont_filter=True,
            )

    def parse_story(self, response: TextResponse) -> Iterable[NewsScrapperItem]:
        """
        Extracts required details from a specific story using xpath
        selectors. A consecutive item object is updated with new required information.

        :param response: An instance of `scrapy.http.TextResponse`
        :return: Iterable of `NewsScrapperItem` object
        """
        # Parse story content using xpath selectors to get story date and the location.
        IndiaTodayParser.CLICKS += 1
        items = response.meta["items"]
        items[ItemField.LOCATION.value] = response.xpath(
            ".//span[@class='jsx-ace90f4eca22afc7 Story_stryloction__IUgpi']/text()"
        ).get()
        items[ItemField.DATE.value] = response.xpath(
            ".//span[@class='jsx-ace90f4eca22afc7 strydate']/text()"
        ).extract()
        yield items
