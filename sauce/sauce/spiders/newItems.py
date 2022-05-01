import time
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy_splash import SplashRequest
from scrapy.utils.project import get_project_settings
import scrapy.utils.misc
import scrapy.core.scraper


class Sac(scrapy.Spider):
    name = "sc2"
    start_urls = ["https://hotshots.inc/", ]
    titles = []
    custom_settings = {
        'FEED_FORMAT': "csv",
        'FEED_URI': "out2.csv"
    }

    Next = []
    links = []



    def parse(self, response):
        new_hot_sauce = response.xpath('//ul[@class="luggage_cat"]/li/a[contains(text(),"New Hot Sauces")]/@href').get()
        yield response.follow(new_hot_sauce, callback=self.filter_stocks)


    def getItems(self,response):
        pass