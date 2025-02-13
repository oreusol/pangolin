"""
This module defines base implementation for any database that will be used
to store the data.
"""

from abc import abstractmethod
import logging
from typing import Optional

from config import get_config_path, load_config
from news_scrapper.log import set_up_logging


class DataBase:
    """
    A simple abstract database class that can be derived
    further to store data to a databse
    """

    def __init__(
        self,
        db_name: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[str] = None,
        table: Optional[str] = None,
    ):
        """Init method"""
        self.log = logging.getLogger()
        config_path = get_config_path()
        config = load_config(config_path=config_path)
        db_config = config.get("database", {})
        log_level = db_config.get("log_level", "INFO")
        log_path = db_config.get("file_name", "database.log")
        set_up_logging(logger=self.log, log_level=log_level, file_name=log_path)
        self.db_name = db_name
        self.connection = None
        self.db_username = username
        self.db_password = password
        self.db_host = host
        self.db_port = port
        self.table = table

    @abstractmethod
    def connect(self):
        """Establishes a connection with database"""
        raise NotImplementedError

    @abstractmethod
    def add(self, params: dict) -> None:
        """Execute an INSERT operation on a database table"""
        raise NotImplementedError

    @abstractmethod
    def close(self):
        """Closes a database connection"""
        raise NotImplementedError
