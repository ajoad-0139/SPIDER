import logging
import os
import sqlite3
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from books_scraper.utils import clean_text, parse_availability, parse_price

logger = logging.getLogger(__name__)


class CleaningPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        title = clean_text(adapter.get("title"))
        if not title:
            raise DropItem(f"Missing title: {adapter.get('product_url')}")

        try:
            price = parse_price(adapter.get("price"))
        except ValueError as exc:
            raise DropItem(f"Invalid price for '{title}': {exc}") from exc

        adapter["title"] = title
        adapter["price"] = price
        adapter["availability"] = parse_availability(adapter.get("availability"))
        adapter["product_url"] = clean_text(adapter.get("product_url"))
        adapter["image_url"] = clean_text(adapter.get("image_url"))
        adapter["category"] = clean_text(adapter.get("category"))

        logger.info("Cleaned item: %s", title)
        return item


class SQLitePipeline:
    CREATE_SQL = """
        CREATE TABLE IF NOT EXISTS books (
            product_url  TEXT PRIMARY KEY,
            title        TEXT NOT NULL,
            price        REAL NOT NULL,
            availability INTEGER NOT NULL,
            image_url    TEXT,
            category     TEXT
        )
    """
    INSERT_SQL = """
        INSERT OR REPLACE INTO books
        (product_url, title, price, availability, image_url, category)
        VALUES (?, ?, ?, ?, ?, ?)
    """

    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get("SQLITE_DB_PATH"))

    def open_spider(self, spider):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute(self.CREATE_SQL)
        self.conn.execute("DELETE FROM books")
        self.conn.commit()
        logger.info("SQLite database ready at %s", self.db_path)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        try:
            self.conn.execute(
                self.INSERT_SQL,
                (
                    adapter["product_url"],
                    adapter["title"],
                    adapter["price"],
                    int(adapter["availability"]),
                    adapter["image_url"],
                    adapter["category"],
                ),
            )
        except sqlite3.Error as exc:
            logger.error("DB insert failed for %s: %s", adapter.get("product_url"), exc)
            raise DropItem(f"Database error: {exc}") from exc
        return item

    def close_spider(self, spider):
        if self.conn:
            self.conn.commit()
            self.conn.close()
            logger.info("SQLite connection closed")