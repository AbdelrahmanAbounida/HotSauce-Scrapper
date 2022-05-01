import time
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy_splash import SplashRequest
from scrapy.utils.project import get_project_settings
import scrapy.utils.misc
import scrapy.core.scraper


class Sac(scrapy.Spider):
    name = "sc"
    start_urls = ["https://hotshots.inc/", ]
    titles = []
    custom_settings = {
        'FEED_FORMAT': "csv",
        'FEED_URI': "out4.csv"
    }

    Next = []
    links = []

    def parse(self, response):
        all_hot_sauces = response.xpath(
            '//ul[@class="luggage_cat"]/li/a[contains(text(),"All Hot Sauces")]/@href').get()
        spicy_products = response.xpath('//*[@id="navbar-collapse-1"]/ul[2]/li/div/div/div/div/div/div/ul/li/a/@href').getall()


        for product in spicy_products:
            yield response.follow(product, callback=self.filter_stocks)

    def filter_stocks(self, response):
        b_instcok = response.xpath(
            '//a[@id="in-stock::7::5ce79257-313a-4e04-9d95-3b5bb00a3780b8934bc5-a0f7-49ba-a588-b1c58dedff31"]/@href').get()
        b_outstock = response.xpath(
            '//a[@id="out-of-stock::7::5ce79257-313a-4e04-9d95-3b5bb00a3780b8934bc5-a0f7-49ba-a588-b1c58dedff31"]/@href').get()

        try:
            yield response.follow(b_instcok, callback=self.inStockProducts)
        except:
            print(f"wrong instock: {response.url}")

        try:
            yield response.follow(b_outstock, callback=self.outStockProducts)
        except:
            print(f"wrong outstock: {response.url}")

    def inStockProducts(self, response):
        try:
            p = response.xpath('//ul[@class="pagination"]')[0]
            pages = p.xpath(".//li/a/@href").getall()[1:-1]
        except:
            pages = []

        titles = response.xpath('//div[@class="caption-title productname text-center"]/text()').getall()
        for title in titles:
            if title not in self.titles:
                self.titles.append(title)
                yield {
                    "Title": title,
                    "Status": "Yes",
                }

        for page in pages:
            if 'javascript' in page:
                continue
            titles = response.xpath('//div[@class="caption-title productname text-center"]/text()').getall()
            for title in titles:
                if title not in self.titles:
                    self.titles.append(title)
                    yield {
                        "Title": title,
                        "Status": "Yes",
                    }

            yield response.follow(page, callback=self.inStockProducts)

        next = response.xpath('//a[@aria-label="Next"]/@href').get()
        if (next is not None) and ('javascript' not in next):
            try:
                yield response.follow(next, callback=self.inStockProducts)
            except:
                print(f"no next here{response.url}")

    def outStockProducts(self, response):
        try:
            p = response.xpath('//ul[@class="pagination"]')[0]
            pages = p.xpath(".//li/a/@href").getall()[1:-1]
        except:
            pages = []

        titles = response.xpath('//div[@class="caption-title productname text-center"]/text()').getall()
        for title in titles:
            if title not in self.titles:
                self.titles.append(title)
                yield {
                    "Title": title,
                    "Status": "No",
                }

        for page in pages:
            if 'javascript' in page:
                continue
            titles = response.xpath('//div[@class="caption-title productname text-center"]/text()').getall()
            for title in titles:
                if title not in self.titles:
                    self.titles.append(title)
                    yield {
                        "Title": title,
                        "Status": "No",
                    }
            yield response.follow(page, callback=self.outStockProducts)
        next = response.xpath('//a[@aria-label="Next"]/@href').get()
        if (next is not None) and (next not in self.Next) and ('javascript' not in next):
            try:
                yield response.follow(next, callback=self.outStockProducts)
            except:
                print(f"no next here{response.url}")
