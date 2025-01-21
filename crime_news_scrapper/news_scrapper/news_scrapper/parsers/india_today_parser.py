import json
from logging import INFO

import scrapy

from news_scrapper.items import NewsScrapperItem
from news_scrapper.parsers.news_website_parser import NewsWebsiteParser
from news_scrapper.const import ItemField
from config import load_config


class IndiaTodayParser(NewsWebsiteParser):
    """Parses data from indianexpress.com website"""

    CLICKS = 0
    LOAD_MORE_CLICKS = 0

    def __init__(self):
        config = load_config(file_path=self.CONFIG_PATH)
        self.config = config.get("india_today_parser", {})
        if self.config:
            log_level = self.config.get("log_level", INFO)
            log_path = self.config.get("file_name", "/home/madhura/projects/pangolin/crime_news_scrapper/india_today.log")
        super().__init__(log_level=log_level, file_name=log_path)
        self.source = "INDIATODAY"

    def parse_front_page(self, response):
        self.logger.info(f"Fetching the data from: {self.source.lower()}.in page")
        # This will parse the front page of indiatoday crime page. xpath selector value
        # "article" will give list of stories. Iterating those can give value for
        # story title, story url and the description by using appropriate selector.
        for crime_news in response.xpath(".//article"):
            news_item = NewsScrapperItem()
            news_item[ItemField.SOURCE.value] = self.source
            news_item[ItemField.TITLE.value] = crime_news.xpath("./div/div/a/@title").get()
            news_item[ItemField.URL.value] = crime_news.xpath("./div/div/a/@href").get()
            news_item[ItemField.DESCRIPTION.value] = crime_news.xpath("./div/div/div/p/text()").get()
            if news_item[ItemField.URL.value] is not None:
                # Again make a request to a specific story in order to get the date and
                # the location associated with it. Pass already created news_item dictionary
                # as its meta field which will be passed in the next request and will be available
                # in the response so that same dictionary can be updated for location and date.
                # filter duplicate links hence dont_filter=False
                self.logger.debug(f"Fetching the data from the story: {news_item[ItemField.URL.value]} page")
                yield response.follow(url=news_item[ItemField.URL.value], callback=self.parse_story,
                                      meta={"items": news_item},
                                      dont_filter=False)

        # Handle the "load more" contents using ajax call.
        # filter duplicate links using dont_filter=False

        # TODO: Rearrange this code
        self.logger.info(f"Loading more contents...")
        # This is the exact call which gets executed after clicking load more.
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
            dont_filter=False,)

    def parse_more_content(self, response):
        # Handle the ajax response from load more request in order to get story
        # title, url and description as earlier.
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
                yield response.follow(url=item[ItemField.URL.value], callback=self.parse_story,
                                      meta={"items": item},
                                      dont_filter=False)

        # Keep checking if there is more content to load and if yes, load and
        # get its data similarly. filter duplicate links
        IndiaTodayParser.LOAD_MORE_CLICKS = response.meta['page']
        self.logger.debug(f"Loading page: {response.meta['page'] + 1}")
        if data.get("data", {}).get("is_load_more", "") and data.get("data", {}).get("is_load_more") == 1:
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
                dont_filter=True,)

    def parse_story(self, response):
        # Parse story content using xpath selectors to get story date and the location.
        IndiaTodayParser.CLICKS += 1
        items = response.meta["items"]
        items[ItemField.LOCATION.value] = response.xpath(".//span[@class='jsx-ace90f4eca22afc7 Story_stryloction__IUgpi']/text()").get()
        items[ItemField.DATE.value] = response.xpath(".//span[@class='jsx-ace90f4eca22afc7 strydate']/text()").extract()
        yield items