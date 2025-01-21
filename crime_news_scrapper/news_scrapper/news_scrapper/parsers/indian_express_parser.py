from logging import INFO
from scrapy_splash import SplashRequest

from news_scrapper.items import NewsScrapperItem
from news_scrapper.parsers.news_website_parser import NewsWebsiteParser
from config import load_config
from news_scrapper.const import ItemField

class IndianExpressParser(NewsWebsiteParser):
    """Parses data from indianexpress.com website"""
    
    LOAD_MORE_CLICKS = 0
    CLICKS = 0

    def __init__(self):
        config = load_config(file_path=self.CONFIG_PATH)
        self.config = config.get("indian_express_parser", {})
        logger_level = INFO
        logger_path = "/home/madhura/projects/pangolin/crime_news_scrapper/indian_express.log"
        if self.config:
            logger_level = self.config.get("log_level", INFO)
            logger_path = self.config.get("file_name", "/home/madhura/projects/pangolin/crime_news_scrapper/indian_express.log")
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
        splash:set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
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

    def parse_front_page(self, response):
        # sends a splash request to already load the data from load more
        self.logger.info(f"Sending the splash request to load all the data from {self.source.lower()}.com page")
        yield SplashRequest(url=response.url, callback=self.parse_data,
                            endpoint='execute',
                            args={'lua_source': self.lua_script, "timeout": 3000},)

    def parse_data(self, response):
        IndianExpressParser.LOAD_MORE_CLICKS = response.data.get('click_count', 0)
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
            news_item[ItemField.DESCRIPTION.value] = story.xpath("./div/p[position()=2]/text()").get()
            news_item[ItemField.LOCATION.value] = ""
            self.seen_urls.add(url)
            if news_item.get(ItemField.URL.value, ""):
                if "/article/cities" in news_item.get("url", ""):
                    news_item[ItemField.LOCATION.value] = news_item[ItemField.URL.value].split("/")[5]
                    yield news_item
                else:
                    # if current page does not contain location and the date info, follow
                    # the story url to get this info.
                    # Filter on duplicate entries
                    yield response.follow(url=news_item[ItemField.URL.value], callback=self.parse_story,
                                      meta={"items": news_item},
                                      dont_filter=False)

    def parse_story(self, response):
        IndianExpressParser.CLICKS += 1
        items = response.meta["items"]
        items[ItemField.LOCATION.value] = response.xpath("normalize-space(.//span[@itemprop='dateModified']/preceding-sibling::text()[1])").get().split("|")[0].strip(" ") or ""
        yield items