import scrapy
from scraper.items import ScraperItem
from scraper.constants import CABA, GBA


class PanaleradeltaSpider(scrapy.Spider):
    name = "panalera_delta"
    allowed_domains = ["panaleradelta.com.ar"]
    start_urls = ["https://panaleradelta.com.ar/product-category/panales-de-bebes/"]
    shipments = CABA + GBA

    def parse(self, response):
        """This function parses a sample response. Some contracts are mingled
        with this docstring.

        @url https://panaleradelta.com.ar/product-category/panales-de-bebes/
        @returns items 1 36
        @returns requests 0 1
        @scrapes description price url image website
        """
        for item in response.xpath("//div[contains(@class, 'product-small')]"):
            description = item.xpath(
                ".//p[contains(@class, 'product-title')]/a/text()"
            ).get()
            price = item.xpath(".//bdi/text()").get()
            url = item.xpath(".//p[contains(@class, 'product-title')]/a/@href").get()
            image = item.xpath(".//div[contains(@class, 'box-image')]//img/@src").get()
            yield ScraperItem(
                description=description,
                price=price,
                url=url,
                image=image,
                website=self.allowed_domains[0],
            )
        next_page = response.xpath("//a[contains(@class, 'next')]/@href").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
