import scrapy
from scraper.items import ScraperItem
from scrapy import Request

from scraper.constants import CABA

BRAND_MAPPING = {
    "categoria%2F33": "pampers",
    "categoria%2F31": "huggies",
    "categoria%2F41": "babysec",
}


class MundoPanalSpider(scrapy.Spider):
    name = "mundo_panal"
    allowed_domains = ["xn--elmundodelpaal-1nb.com.ar"]
    custom_settings = {"LOG_FILE": "logs/mundo_panal.log", "LOG_LEVEL": "DEBUG"}
    urls = {
        "pampers": "https://xn--elmundodelpaal-1nb.com.ar/#!/categoria/33/pagina/{}/",
        "huggies": "https://xn--elmundodelpaal-1nb.com.ar/#!/categoria/31/pagina/{}/",
        "babysec": "https://xn--elmundodelpaal-1nb.com.ar/#!/categoria/41/pagina/{}/",
    }
    shipments = CABA

    def __init__(self, page_size=None, *args, **kwargs):
        super(MundoPanalSpider, self).__init__(*args, **kwargs)
        self._current_page = {brand: 0 for brand in self.urls.keys()}

    def next_page(self, brand):
        curr_page = self._current_page[brand]
        url = self.urls[brand].format(curr_page)
        request = scrapy.Request(url)
        self._current_page[brand] += 1
        return request

    def start_requests(self):
        for brand in self.urls.keys():
            yield self.next_page(brand)

    def populate_item(self, response):
        price = response.xpath(
            "//span[contains(@class, 'precio-importe-int')]/text()"
        ).get()
        url = response.url
        image = response.xpath("//div[contains(@class, 'detalle')]//img/@src").get()
        description_title = response.xpath(
            "//span[contains(@class, 'producto-descripcion')]/text()"
        ).get()
        sizes = False
        for description in response.xpath(
            "//div[contains(@class, 'producto-agregar-al-carro')]//a/text()"
        ):
            sizes = True
            yield ScraperItem(
                description=description.get(),
                price=price,
                url=url,
                image=image,
                website=self.allowed_domains[0],
                brand=None,
                size=None,
                target_kg=None,
                units=None,
            )
        if not sizes:
            yield ScraperItem(
                description=description_title,
                price=price,
                url=url,
                image=image,
                website=self.allowed_domains[0],
                brand=None,
                size=None,
                target_kg=None,
                units=None,
            )

    def _get_brand(self, url):
        for brand_mapping, brand in BRAND_MAPPING.items():
            if brand_mapping in url:
                return brand
        raise Exception("Brand not found")

    def parse(self, response):
        """This function parses a sample response. Some contracts are mingled
        with this docstring.

        @url https://xn--elmundodelpaal-1nb.com.ar/#!/categoria/33/pagina/0/
        @returns requests 0 19
        @scrapes description price url image website
        """
        brand = self._get_brand(response.url)
        items = response.xpath("//div[contains(@class, 'wdg-producto')]")
        for item in items:
            follow_url = item.xpath(".//a/@href").get()
            url = f"https://xn--elmundodelpaal-1nb.com.ar/{follow_url}"
            yield Request(url, callback=self.populate_item)
        if items:
            yield self.next_page(brand)
