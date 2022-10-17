import scrapy
from scraper.items import ScraperItem


class TravesurasonlineSpider(scrapy.Spider):
    name = 'travesurasonline'
    allowed_domains = ['travesurasonline.sed.com.ar']
    start_urls = ['https://travesurasonline.sed.com.ar/catalogo;r=pa%C3%B1al%20bebe;s=otros;clear=true']

    def __init__(self, *args, **kwargs):
        super(TravesurasonlineSpider, self).__init__(*args, **kwargs)
        self._current_page = 0

    def start_requests(self):
        yield self.next_page()

    def next_page(self):
        request = scrapy.FormRequest(
            url="https://travesurasonline.sed.com.ar/API/productos/listar",
            formdata={
                "indice": "clasificados",
                "pagina": str(self._current_page),
                "sort": "Recientes",
                "aggs_limit": "150",
                "size": "36",
                "r": "pañal bebe",
                "s": "otros",
                "ampliarvendedor": "true",
            }
        )
        self._current_page += 1
        return request

    def parse(self, response):
        """This function parses a sample response. Some contracts are mingled
        with this docstring.

        @url https://panaleradelta.com.ar/product-category/panales-de-bebes/
        @returns items 1 36
        @returns requests 0 1
        @scrapes description price url image website
        """
        items = response.json().get("datos", [])
        for item in items:
            description = item.get("titulo")
            price = item.get("precio", "")[1:]
            brand = item.get("marca")
            url = "https://travesurasonline.sed.com.ar/pa%C3%B1al%20bebe/" + item.get("post_name")
            image = item.get("portada")
            yield ScraperItem(
                description=description,
                price=price,
                url=url,
                image=image,
                website=self.allowed_domains[0],
                brand=brand,
                size=None,
                target_kg=None,
                units=None,
            )
        if items:
            yield self.next_page()

