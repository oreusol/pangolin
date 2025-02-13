"""
A simple python class which processes a scraped item and
stores it in a database.
"""

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging
import sys
from itemadapter import ItemAdapter

from config import get_config_path, load_config
from news_scrapper.database.postgresql import PostgreSQLDB
from news_scrapper.log import set_up_logging
from news_scrapper.items import NewsScrapperItem


class NewsScrapperStoragePipeline:
    """
    Initializes a :py:class:`NewsScrapperStoragePipeline` object.
    Helps in storing the scraped item in a database
    """

    def __init__(self):
        self.db = None
        self.log = logging.getLogger()

    def open_spider(self, spider):
        """
        This method is called when the spider is opened. It reads the
        database config and establishes a connection with a database
        """
        config_path = get_config_path()
        config = load_config(config_path=config_path)
        db_config = config.get("database", {})
        pipeline_config = config.get("pipeline", {})
        for config_key, config_val in db_config.items():
            globals()[config_key] = config_val
        log_level = pipeline_config.get("log_level", "INFO")
        log_path = pipeline_config.get("file_name", "pipeline.log")
        set_up_logging(logger=self.log, log_level=log_level, file_name=log_path)
        self.log.info("Initializing the database client")
        self.db = PostgreSQLDB(
            db_name=db_name, username=username, host=host, port=port, table=table_name
        )

    def process_item(self, item, spider) -> NewsScrapperItem:
        """
        Processes an item received from Item loader to further
        add it into the database table.
        :param item: a scraped `scrapy.Item` object
        :param spider: spider (`Spider` object) the spider which was opened
        ::return: `NewsScrapperItem` object
        """
        try:
            self.log.info("Processing an item to store it into the database table")
            self.db.add(params=item)
            return item
        except Exception as err:
            sys.exit()

    def close_spider(self, spider):
        """This method is called when the spider is closed.
        :param spider: spider (`Spider` object) the spider which was closed
        """
        self.log.info("Closing the database connection")
        self.db.close()
