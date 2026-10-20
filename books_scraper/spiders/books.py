import random
import scrapy
from books_scraper.items import BookItem
from books_scraper.utils import clean_text


class BooksSpider(scrapy.Spider):

    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/index.html"]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        settings = crawler.settings
        spider.category_min = settings.getint("CATEGORY_SAMPLE_MIN", 5)
        spider.category_max = settings.getint("CATEGORY_SAMPLE_MAX", 10)
        spider.books_per_category = settings.getint("BOOKS_PER_CATEGORY", 5)
        spider.random_generator = random.Random()
        return spider

    def parse(self, response):
        links = response.css("div.side_categories ul.nav-list > li > ul > li > a")
        categories = []
        for link in links:
            name = clean_text(link.css("::text").get())
            url = response.urljoin(link.attrib["href"])
            categories.append((name, url))

        self.logger.info("Discovered %d categories", len(categories))
        sample_size = min( self.random_generator.randint(self.category_min, self.category_max), len(categories))
        selected = self.random_generator.sample(categories, sample_size)
        self.logger.info("Selected %d categories: %s", sample_size, [name for name, _ in selected])

        for name, url in selected:
            yield scrapy.Request( url, callback=self.parse_category, cb_kwargs={"category": name, "book_urls": []})

    def parse_category(self, response, category, book_urls):
        for href in response.css("article.product_pod h3 a::attr(href)").getall():
            url = response.urljoin(href)
            book_urls.append(url)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow( next_page, callback=self.parse_category, cb_kwargs={"category": category, "book_urls": book_urls})
            return

        count = min(self.books_per_category, len(book_urls))
        self.logger.info("Category '%s': %d books found, sampling %d", category, len(book_urls), count)

        sampled = self.random_generator.sample(book_urls, count)
        for url in sampled:
            yield scrapy.Request( url, callback=self.parse_book, cb_kwargs={"category": category})

    def parse_book(self, response, category):
        item = BookItem()
        item["title"] = response.css("div.product_main h1::text").get()
        item["price"] = response.css("p.price_color::text").get()
        item["availability"] = response.xpath( "normalize-space(//p[contains(@class,'availability')])").get()
        item["product_url"] = response.url
        item["image_url"] = response.urljoin(response.css("div.item.active img::attr(src)").get())
        item["category"] = category
        self.logger.info("Scraped book: %s", item["title"])
        yield item