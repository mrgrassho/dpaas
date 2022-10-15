from typing import List, Dict
import scrapy
from scraper import settings
import lxml.html

from scraper.items import ScraperItem


class TiendaNubeSpider(scrapy.Spider):
    url = "https://tienda-nube-ecommerce.com/panales/bebes"
    custom_settings = {
        "LOG_LEVEL": "DEBUG"
    }
    items_xpath = "//div[contains(@class,'item-product')]"

    def __init__(self, page_size=None, *args, **kwargs):
        super(TiendaNubeSpider, self).__init__(*args, **kwargs)
        self._current_page = 0
        self._page_size = page_size or settings.TIENDA_NUBE_PAGE_SIZE

    def next_page(self):
        self._current_page += 1
        return scrapy.Request(
            f"{self.url}/page/{self._current_page}/?results_only=true&limit={self._page_size}",
            headers={"Accept": "application/json, text/javascript, */*; q=0.01"},
        )

    def start_requests(self):
        yield self.next_page()

    def extract_item_data(self, item: lxml.html.HtmlElement) -> Dict:
        # Complete this function with item data
        #
        # Example:
        #   ...
        #   json_raw = item.xpath(".//script/text()")[0]
        #   return json.loads(json_raw)
        return {}

    def extract_variants_data(self, item: lxml.html.HtmlElement) -> List[Dict]:
        # Complete this function with variants data
        #
        # Example:
        #   ...
        #   json_raw = item.xpath(".//div[1]/@data-variants")[0]
        #   return json.loads(json_raw)
        return [{}]

    def item(self, common, variant):
        return ScraperItem()

    def parse(self, response):
        raw_html = response.json().get("html", "")
        html_response = lxml.html.fromstring(raw_html)
        for item in html_response.xpath(self.items_xpath):
            common = self.extract_item_data(item)
            for variant in self.extract_variants_data(item):
                yield self.item(common, variant)
        if response.json().get("has_next"):
            yield self.next_page()
