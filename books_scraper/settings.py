
BOT_NAME = "books_scraper"

SPIDER_MODULES = ["books_scraper.spiders"]
NEWSPIDER_MODULE = "books_scraper.spiders"

ADDONS = {}

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

FEED_EXPORT_ENCODING = "utf-8"


CATEGORY_SAMPLE_MIN = 5
CATEGORY_SAMPLE_MAX = 10
BOOKS_PER_CATEGORY = 5
RANDOM_SEED = None  

LOG_LEVEL = "INFO"
DOWNLOAD_DELAY = 0.25


import os

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.path.abspath("output"))
SQLITE_DB_PATH = os.path.join(OUTPUT_DIR, "books.db")

ITEM_PIPELINES = {
    "books_scraper.pipelines.CleaningPipeline": 300,
    "books_scraper.pipelines.SQLitePipeline": 400,
}

FEED_EXPORT_FIELDS = [
    "title", "price", "availability", "product_url", "image_url", "category",
]

FEEDS = {
    os.path.join(OUTPUT_DIR, "books.json"): {
        "format": "json",
        "indent": 2,
        "overwrite": True,
    },
    os.path.join(OUTPUT_DIR, "books.csv"): {
        "format": "csv",
        "overwrite": True,
    },
    os.path.join(OUTPUT_DIR, "books.xml"): {
        "format": "xml",
        "item_element": "book",
        "root_element": "books",
        "overwrite": True,
    },
}