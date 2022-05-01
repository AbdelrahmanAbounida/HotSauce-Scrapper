import scrapy
import scrapy.core.scraper
from scrapy.crawler import CrawlerProcess
from scrapy_splash import SplashRequest
from scrapy.utils.project import get_project_settings

class HotSauce(scrapy.Spider):
    name = "test"
    start_urls = ["https://hotshots.inc/", ]
    titles = []
    custom_settings = {
        'FEED_FORMAT': "csv",
        'FEED_URI': "sauces.csv"
    }
    Next = []

    ##########################################################
    ## Generate Links ##
    ##########################################################
    def parse(self, response):
        all_hot_sauces = response.xpath(
            '//ul[@class="luggage_cat"]/li/a[contains(text(),"All Hot Sauces")]/@href').get()
        new_hot_sauce = response.xpath('//ul[@class="luggage_cat"]/li/a[contains(text(),"New Hot Sauces")]/@href').get()
        spicy_products = response.xpath(
            '//*[@id="navbar-collapse-1"]/ul[2]/li/div/div/div/div/div/div/ul/li/a/@href').getall()

        a = self.start_urls[0] + all_hot_sauces
        b = self.start_urls[0] + new_hot_sauce

        yield response.follow(a, callback=self.filter_stocks, meta={"cat": 'Hot Sauce'})
        yield response.follow(b, callback=self.new_items, meta={"cat": 'New Product'})

        for cat in spicy_products:
            b = self.start_urls[0] + cat
            yield response.follow(b, callback=self.filter_stocks, meta={"cat": 'Spicy Product'})

    ##########################################################
    ## Filter in & out stocks ##
    ##########################################################

    def new_items(self, response):
        pass

    def filter_stocks(self, response):
        b_instcok = response.xpath(
            '//a[@id="in-stock::7::5ce79257-313a-4e04-9d95-3b5bb00a3780b8934bc5-a0f7-49ba-a588-b1c58dedff31"]/@href').get()
        b_outstock = response.xpath(
            '//a[@id="out-of-stock::7::5ce79257-313a-4e04-9d95-3b5bb00a3780b8934bc5-a0f7-49ba-a588-b1c58dedff31"]/@href').get()

        try:
            instock_link = self.start_urls[0] + b_instcok
            yield response.follow(instock_link, callback=self.inStockProducts, meta={'cat': response.meta['cat']})
        except:
            print(f"no instock link: {response.url}")

        try:
            outstock_link = self.start_urls[0] + b_outstock
            yield response.follow(outstock_link, callback=self.outStockProducts, meta={'cat': response.meta['cat']})
        except:
            print(f"no outstock link: {response.url}")

    ##########################################################
    ## Generate instock products ##
    ##########################################################
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
                    "Category": response.meta['cat'],
                }
        print(len(self.titles))

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
                        "Category": response.meta['cat'],
                    }
            print(len(self.titles))

            yield response.follow(self.start_urls[0] + page, callback=self.inStockProducts,
                                  meta={'cat': response.meta['cat']})

        next = response.xpath('//a[@aria-label="Next"]/@href').get()
        if (next is not None) and (next not in self.Next) and ('javascript' not in next):
            try:
                self.Next.append(next)
                l = self.start_urls[0] + next
                yield response.follow(l, callback=self.inStockProducts, meta={'cat': response.meta['cat']})
            except:
                print(f"no next here{response.url}")

    ##########################################################
    ## Generate outstock products ##
    ##########################################################

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
                    "Category": response.meta['cat'],
                }
        print(len(self.titles))

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
                        "Category": response.meta['cat'],
                    }
            print(len(self.titles))

            yield response.follow(self.start_urls[0] + page, callback=self.outStockProducts,
                                  meta={"cat": response.meta['cat']})
        next = response.xpath('//a[@aria-label="Next"]/@href').get()
        if (next is not None) and (next not in self.Next) and ('javascript' not in next):
            try:
                self.Next.append(next)
                l = self.start_urls[0] + next
                yield response.follow(l, callback=self.outStockProducts, meta={"cat": response.meta['cat']})
            except:
                print(f"no next here{response.url}")

if __name__ == "__main__":
    print("Lets Gooooooo!!!")
    process = CrawlerProcess(get_project_settings())
    process.crawl(HotSauce)
    process.start()
