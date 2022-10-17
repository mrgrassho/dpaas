import scrapy
from scraper.items import ScraperItem


class CotodigitalSpider(scrapy.Spider):
    name = 'cotodigital'
    allowed_domains = ['www.cotodigital3.com.ar']
    start_urls = ["https://www.cotodigital3.com.ar/sitios/cdigi/browse/catalogo-perfumer%C3%ADa-pa%C3%B1ales-y-productos-para-incontinencia-pa%C3%B1ales-para-beb%C3%A9/_/N-fmf3uu"]
    page_size = 48

    def __init__(self, *args, **kwargs):
        super(CotodigitalSpider, self).__init__(*args, **kwargs)
        self._current_page = 0

    def next_page(self):
        size = self._current_page * self.page_size
        url = f"https://www.cotodigital3.com.ar/sitios/cdigi/browse/catalogo-perfumer%C3%ADa-pa%C3%B1ales-y-productos-para-incontinencia-pa%C3%B1ales-para-beb%C3%A9/_/N-fmf3uu?No={size}"
        request = scrapy.Request(url)
        self._current_page += 1
        return request

    def start_requests(self):
        yield self.next_page()

    def parse(self, response):
        """This function parses a sample response. Some contracts are mingled
        with this docstring.

        @url https://www.cotodigital3.com.ar/sitios/cdigi/browse/catalogo-perfumer%C3%ADa-pa%C3%B1ales-y-productos-para-incontinencia-pa%C3%B1ales-para-beb%C3%A9/_/N-fmf3uu?No=0
        @returns items 1 48
        @returns requests 0 1
        @scrapes description price url image website
        """
        items = response.xpath("//li[contains(@class, 'clearfix')]")
        for item in items:
            description = item.xpath(".//div[contains(@class, 'descrip_full')]/text()").get()
            price = item.xpath(".//span[contains(@class, 'atg_store_newPrice')]/text()").get().strip()[1:]
            image = item.xpath(".//span[contains(@class, 'atg_store_productImage')]/img/@src").get()
            url = self.allowed_domains[0] + item.xpath(".//div[contains(@class, 'product_info_container')]/a/@href").get()
            yield ScraperItem(
                description=description,
                price=price,
                url=url,
                image=image,
                website=self.allowed_domains[0],
                brand=None,
                size=None,
                target_kg=None,
                units=None,
            )
        if items:
            yield self.next_page()
