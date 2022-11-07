import scrapy
from scraper.items import ScraperItem


class JumboSpider(scrapy.Spider):
    name = 'jumbo'
    allowed_domains = ['www.jumbo.com.ar']

    def __init__(self, *args, **kwargs):
        super(JumboSpider, self).__init__(*args, **kwargs)
        self._current_page = 1

    def next_page(self):
        url = f"https://www.jumbo.com.ar/buscapagina?sl=1579df47-6ea5-4570-a858-8067a35362be&PS=18&cc=18&sm=0&PageNumber={self._current_page}&&fq=C%3a%2f457%2f10014%2f&O=OrderByScoreDESC"
        request = scrapy.Request(url)
        self._current_page += 1
        return request

    def start_requests(self):
        yield self.next_page()

    def parse(self, response):
        """This function parses a sample response. Some contracts are mingled
        with this docstring.

        @url https://www.jumbo.com.ar/buscapagina?sl=1579df47-6ea5-4570-a858-8067a35362be&PS=18&cc=18&sm=0&PageNumber=1&&fq=C%3a%2f457%2f10014%2f&O=OrderByScoreDESC
        @returns requests 0 1
        @returns items 0 19
        @scrapes description price url image website
        """
        items = response.xpath("//li[contains(@class, 'bebes-y-ninos---jumbo')]")
        for item in items:
            description = item.xpath(".//h2[contains(@class, 'product-item__name')]/a/text()").get()
            price = item.xpath(".//span[contains(@class, 'product-prices__value')]/text()").get()[2:]
            url = item.xpath(".//h2[contains(@class, 'product-item__name')]/a/@href").get()
            image = item.xpath(".//a[contains(@class, 'product-item__image-link')]/img/@src").get()
            yield ScraperItem(
                description=description,
                price=price,
                url=url,
                image=image,
                website=self.allowed_domains[0],
            )
        if items:
            yield self.next_page()

