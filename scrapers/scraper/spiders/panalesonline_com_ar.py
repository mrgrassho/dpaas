import json
from typing import List, Dict
import lxml.html

from scraper.items import ScraperItem
from scraper.spiders.tiendanube import TiendaNubeSpider


class PanalesonlineComArSpider(TiendaNubeSpider):
    name = "panalesonline_com_ar"
    allowed_domains = ["www.panalesonline.com.ar"]
    url = "https://www.panalesonline.com.ar/panales/bebes"
    custom_settings = {
        "LOG_LEVEL": "DEBUG"
    }

    def extract_item_data(self, item: lxml.html.HtmlElement) -> Dict:
        json_raw = item.xpath(".//script/text()")[0]
        return json.loads(json_raw)

    def extract_variants_data(self, item: lxml.html.HtmlElement) -> List[Dict]:
        json_raw = item.xpath(".//div[1]/@data-variants")[0]
        return json.loads(json_raw)

    def item(self, common, variant):
        return ScraperItem(
            description=common.get("name"),
            price=variant.get("price_number"),
            url=common.get("offers", {}).get("url"),
            image=common.get("image"),
            website=self.allowed_domains[0],
            brand=None,
            size=variant.get("option0"),
            target_kg=None,
            units=variant.get("option1"),
        )
