"""
This module provides functionality to store the data to a PostgreSQL database.

How To Use This Module
======================

For example:
1. Import class :py:class:`PostgreSQLDB`:
   ``from news_scrapper.database.postgresql import PostgreSQLDB``.

2. Initialize class:
   postgres_db = PostgreSQLDB()

3. Start using its methods:
   postgres_db.connect()
"""

import os
import psycopg2

from news_scrapper.database.database import DataBase


class PostgreSQLDB(DataBase):
    """
    Initializes a :py:class:`PostgreSQLDB` object.
    Defines a behaviour for storing data to PostgreSQL database

    ::return: a new :py:class:`PostgreSQLDB` object
    """

    def __init__(self, db_name, *args, **kwargs):
        password = os.environ.get("DB_PASSWORD")
        super().__init__(db_name=db_name, password=password, *args, **kwargs)
        self.connection = self.connect()
        self.cursor = self.connection.cursor()
        self.create_table(self.table)

    def connect(self) -> None:
        """
        Establishes an actual conncetion with postgresql database using psycopg2 module
        """
        self.log.info("Establishing a connection with database: %s", self.db_name)
        try:
            return psycopg2.connect(
                database=self.db_name,
                user=self.db_username,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port,
            )
        except psycopg2.Error as err:
            self.log.error("Error establishing a database connection: %s", err)
            raise

    def create_table(self, table_name: str) -> None:
        """
        Creates a table with rows as ID(auto incremented primary key), source, title,
        description, url, location, date all as string.
        :param table_name: table name to create.
        """
        self.log.info("Creating a table: %s", table_name)
        try:
            self.cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {table_name}
                (
                    ID SERIAL PRIMARY KEY,
                    source TEXT,
                    title TEXT UNIQUE,
                    description TEXT UNIQUE,
                    url TEXT UNIQUE,
                    location text,
                    date TEXT
                )
            """
            )
            self.connection.commit()
        except psycopg2.Error as err:
            self.log.error("Table creation failed: %s", err)
            self.connection.rollback()

    def add(self, params: dict) -> None:
        """
        Performs insert operation for a table. Inserts source, title, description,
        url, location and the date values to a database table.
        :param params: dict of values to be inserted
        """
        self.log.debug("Executing Insert")
        try:
            self.cursor.execute(
                f"""
            INSERT INTO {self.table} (source, title, description, url, location, date)
            VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    params["source"],
                    params["title"],
                    params["description"],
                    params["url"],
                    params["location"],
                    params["date"],
                ),
            )
            self.connection.commit()
        except Exception as err:
            self.log.error("Insert Failed: %s %s", err, params)
            self.connection.rollback()
            raise err

    def close(self) -> None:
        """Closes the database connection"""
        self.cursor.close()
        self.connection.close()
