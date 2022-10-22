import scrapy
from scraper.constants import DiaperBrand
from scraper.items import ScraperItem

class MeliSpider(scrapy.Spider):
    name = 'meli'
    allowed_domains = ['mercadolibre.com.ar']
    start_urls = ['http://listado.mercadolibre.com.ar']
    custom_settings = {"LOG_FILE": "logs/meli.log", "LOG_LEVEL": "DEBUG"}
    path = '/bebes/higiene-cuidado-bebe/panales/descartables/{brand}/panales{from_page}_NoIndex_True'
    page_size = 50
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'
    }

    def __init__(self, *args, **kwargs):
        super(MeliSpider, self).__init__(*args, **kwargs)
        self._current_page = {brand: 0 for brand in DiaperBrand.brands()}

    def _prepare_next_page(self, brand, item_count):
        from_page = ''
        if item_count > 0:
            from_page = f'_Desde_{item_count+1}'
        return self.start_urls[0] + self.path.format(brand=brand, from_page=from_page)

    def next_page(self, brand):
        item_count = self._current_page[brand] * self.page_size
        url = self._prepare_next_page(brand, item_count)
        request = scrapy.Request(url, headers=self.headers)
        self._current_page[brand] += 1
        return request

    def start_requests(self):
        for brand in DiaperBrand.brands():
            yield self.next_page(brand)

    def extract_item(self, response):
        description = response.xpath('//h1[contains(@class, "ui-pdp-title")]/text()').get()
        image = response.xpath('//figure[contains(@class, "ui-pdp-gallery__figure")]/img/@src').get()
        size = None
        units = None
        brand = None
        attrb = response.xpath('//span[contains(@class, "ui-pdp-variations__selected-text")]/text()')
        if len(attrb) >= 2:
            size = attrb[0].get()
            units = attrb[1].get()
        try:
            brand = response.xpath('//span[@class="andes-table__column--value"]/text()')[0].get().lower()
        except Exception:
            pass
        price = response.xpath('//meta[@itemprop="price"]/@content').get()
        yield ScraperItem(
            description=description,
            price=price,
            url=response.url,
            image=image,
            website=self.allowed_domains[0],
            brand=brand,
            size=size,
            target_kg=None,
            units=units,
        )

    def _follow(self, response, callback, index):
        try:
            container = response.xpath('//div[contains(@class, "ui-pdp-variations__picker")]')
            urls = container[index].xpath('.//a/@href')
            if not urls:
                raise IndexError("No results")
            yield from response.follow_all(urls, callback=callback, headers=self.headers)
        except IndexError:
            yield from (self.extract_item(response))

    def follow_available_qtys(self, response):
        yield from self._follow(response, callback=self.extract_item, index=0)

    def follow_available_sizes(self, response):
        yield from self._follow(response, callback=self.follow_available_qtys, index=1)

    def parse(self, response):
        """This function parses a sample response. Some contracts are mingled
        with this docstring.

        @url https://www.jumbo.com.ar/buscapagina?sl=1579df47-6ea5-4570-a858-8067a35362be&PS=18&cc=18&sm=0&PageNumber=1&&fq=C%3a%2f457%2f10014%2f&O=OrderByScoreDESC
        @returns requests 0 1
        @returns items 0 19
        @scrapes description price url image website
        """
        item_urls = response.xpath('//a[contains(@class, "ui-search-item__group__element")]/@href')
        yield from response.follow_all(item_urls, callback=self.follow_available_sizes, headers=self.headers)
        # if item_urls:
        #     yield self.next_page()
