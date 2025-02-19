# pangolin
An application to scrap the data from news sites.


# Overview
pangolin is a crime news web scrapper which crawls different news websites and extracts structured data from web pages. Underneath, it uses [scrapy](https://github.com/scrapy/scrapy) framework to crawl and scrap the data. The scraped data then stored to the database.


# Requirements
- python 3.12+
- linux
- docker
- postgreSQL [Download postgreSQL](https://www.postgresql.org/download/)


# Pre-install
Before going for actual installation, make sure to configure following things:

1. Clone pangoline repo: [pangoline].(https://github.com/oreusol/pangolin)
	`git clone https://github.com/oreusol/pangolin.git`

2. Start scrapy-splash server. [scrapy-splash](https://github.com/scrapy-plugins/scrapy-splash).
    `docker run --rm -p 8050:8050 scrapinghub/splash --max-timeout 3600`

2. Create a user and the database in postgresql.

3. Update postgresql password for the username in the environment varialble **DB_PASSWORD**.
    `export DB_PASSWORD=<password>`

4. Either create your own configuration as given in config.yaml or modify the config file as per your details such as database user credentials, table name, log level, log path etc.
	- Specify the path of your configuration file in settings.yaml as
	  **CUSTOM_CONFIG_PATH** or as a environment variable    **CUSTOM_CONFIG_PATH**

5. Install postgreSQL development libraries needed to compile psycopg2.
    `sudo apt update`
    `sudo apt install libpq-dev python3-dev`

# Install

1. Create a new virtual environment and activate it.

3. Install all the requirements (in a virtual environment).
	`pip install -r crime_news_scrapper/requirements.txt`

4. Move to the scrapy project directory.
	`cd crime_news_scrapper/news_scrapper`

5. Start the crawl to scrap the data from news websites.
	`scrapy crawl news_spider`