"""
This module helps in parsing the response for `www.indianexpress.com/about/crime-news`
page. Each crime story from the response will be parsed in order to get required items
and those items will be returned one by one.

How To Use This Module
======================

1. Import class :py:class:`IndianExpressParser`:
    from news_scrapper.parsers.indian_express_parser import IndianExpressParser

2. Instantiate the class as::
   indian_express = IndianExpressParser()

3. Start parsing by using:
   self.indian_express.parse_front_page(response=response)

"""

from typing import Iterable, Union

from scrapy_splash import SplashRequest
from scrapy.http import Request
from scrapy.http import TextResponse

from config import get_config_path, load_config
from ..items import NewsScrapperItem
from ..parsers.news_website_parser import NewsWebsiteParser
from ..const import ItemField


class IndianExpressParser(NewsWebsiteParser):
    """
    Initializes a :py:class:`IndianExpressParser` object.
    Defines parsing mechanism to parse the response received from
    `www.indianexpress.com/about/crime-news`.

    ::return: a new :py:class:`IndianExpressParser` object
    """

    LOAD_MORE_CLICKS = 0
    CLICKS = 0

    def __init__(self):
        """
        Reads the config and initializes basic parsing logic
        """
        config_path = get_config_path()
        config = load_config(config_path=config_path)
        self.config = config.get("indian_express_parser", {})
        logger_level = "INFO"
        logger_path = "indian_express.log"
        if self.config:
            logger_level = self.config.get("log_level", "INFO")
            logger_path = self.config.get("file_name", "indian_express.log")
        super().__init__(log_level=logger_level, file_name=logger_path)
        self.seen_urls = set()
        self.source = "TheIndianEXPRESS"

    # Lua script to handle button click event for Load more button on the web page
    # This script checks for the button with id ""button#load_tag_article", if present
    # will perform mouse click event till the last load more is not hit and after this
    # will return whole html data that was loaded by all these clicks.
    lua_script = """
    function main(splash, args)
        -- Set the user agent
        splash:set_user_agent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)" ..
            "Chrome/91.0.4472.124 Safari/537.36"
        )

        -- Navigate to the provided URL
        assert(splash:go(args.url))
        assert(splash:wait(3))  -- Wait for the page to fully load

        -- Initialize variables
        local previous_content = ""
        local current_content = splash:html()
        local click_count = 0  -- Counter for how many times the button was clicked

        -- Loop to click the "Load More" button until no new content is loaded
        while previous_content ~= current_content do
            previous_content = current_content

            -- Select the "Load More" button using its class or ID
            local button = splash:select("button#load_tag_article")  -- Using ID selector
            if button then
                button:mouse_click()  -- Simulate the button click
                assert(splash:wait(3))  -- Wait for the new content to load
                click_count = click_count + 1
            else
                break  -- Exit if the button is not found
            end

            -- Update the current page content
            current_content = splash:html()
        end

        -- Return the final loaded page content
        return {
            html = splash:html(),
            click_count = click_count,
        }
        end
    """

    def parse_front_page(self, response: TextResponse) -> SplashRequest:
        """
        This method uses scrapy-splash framework and sends a SplashRequest to
        first load all the contents(executes all load more) from the response page
        using a lua script. After that, given callback will be executed for further parsing.
        :param response: An instance of `scrapy.http.TextResponse`
        ::return: An iterable of `scrapy_splash.SplashRequest` response
        """
        # sends a splash request to already load the data from load more
        self.logger.info(
            f"Sending the splash request to load all the data from {self.source.lower()}.com page"
        )
        yield SplashRequest(
            url=response.url,
            callback=self.parse_data,
            endpoint="execute",
            args={"lua_source": self.lua_script, "timeout": 3000},
        )

    def parse_data(self, response: TextResponse) -> Iterable[Union[NewsScrapperItem, Request]]:
        """
        Iterates over each story from response and extract required details using xpath
        selectors. Each story response will be modelled as an instance of `NewsScrapperItem`.
        If certain information is not available, makes a scrapy request again to each specific
        story url.
        :param response: An instance of `scrapy.http.TextResponse`
        :return: Iterable of `NewsScrapperItem` object or Iterable of `scrapy.http.Request` object
        """
        IndianExpressParser.LOAD_MORE_CLICKS = response.data.get("click_count", 0)
        self.logger.info(f"Total Load more clicks: {IndianExpressParser.LOAD_MORE_CLICKS}")
        # once load more is done, response is received and parsed in order to get title, url,
        # description, location and the date of the story using xpath selectors.
        for story in response.xpath("//div[@class='details']"):
            news_item = NewsScrapperItem()
            url = story.xpath("./div/h3/a/@href").get()
            # Keep a track of already visited URLs in order to avoid duplication.
            if self.seen_urls:
                if url in self.seen_urls:
                    self.logger.info(f"This data is already scrapped: {url}. Hence continuing...")
                    continue
            news_item[ItemField.SOURCE.value] = self.source
            news_item[ItemField.TITLE.value] = story.xpath("./div/h3/a/text()").get()
            news_item[ItemField.DATE.value] = story.xpath("./div/p/text()").get()
            news_item[ItemField.URL.value] = url
            news_item[ItemField.DESCRIPTION.value] = story.xpath(
                "./div/p[position()=2]/text()"
            ).get()
            news_item[ItemField.LOCATION.value] = ""
            self.seen_urls.add(url)
            if news_item.get(ItemField.URL.value, ""):
                if "/article/cities" in news_item.get("url", ""):
                    news_item[ItemField.LOCATION.value] = news_item[ItemField.URL.value].split("/")[
                        5
                    ]
                    yield news_item
                else:
                    # if current page does not contain location and the date info, follow
                    # the story url to get this info.
                    # Filter on duplicate entries
                    yield response.follow(
                        url=news_item[ItemField.URL.value],
                        callback=self.parse_story,
                        meta={"items": news_item},
                        dont_filter=False,
                    )

    def parse_story(self, response: TextResponse) -> Iterable[NewsScrapperItem]:
        """
        Extracts required details from a specific story using xpath
        selectors. A consecutive item object is updated with new required information.

        :param response: An instance of `scrapy.http.TextResponse`
        :return: Iterable of `NewsScrapperItem` object
        """
        IndianExpressParser.CLICKS += 1
        items = response.meta["items"]
        items[ItemField.LOCATION.value] = (
            response.xpath(
                "normalize-space(.//span[@itemprop='dateModified']/preceding-sibling::text()[1])"
            )
            .get()
            .split("|")[0]
            .strip(" ")
            or ""
        )
        yield items
