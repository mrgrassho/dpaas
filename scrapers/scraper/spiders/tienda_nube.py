import json
from re import match
import scrapy
from scraper import settings
import lxml.html

from scraper.items import ScraperItem
from scraper.constants import CABA, GBA, ROSARIO, SAN_JUAN, SANTA_CRUZ, SANTA_ROSA


class TiendaNubeSpider(scrapy.Spider):
    url = "https://tienda-nube-ecommerce.com/panales/bebes"
    custom_settings = {"LOG_LEVEL": "DEBUG"}
    items_xpath = "//div//script/text()"
    variants_xpath = "//div/@data-variants"

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

    def item(self, common, variant):
        return ScraperItem(
            description=common.get("name"),
            price=variant.get("price_number"),
            url=common.get("offers", {}).get("url"),
            image=common.get("image"),
            website=self.allowed_domains[0],
            brand=None,
            size=variant.get("option0"),
            units=variant.get("option1"),
        )

    def parse(self, response):
        raw_html = response.json().get("html", "")
        html_response = lxml.html.fromstring(raw_html)
        commons = html_response.xpath(self.items_xpath)
        variants = html_response.xpath(self.variants_xpath)
        if not variants:
            for common in commons:
                common_json = json.loads(common)
                yield self.item(common_json, {})
        else:
            for common, variant in zip(commons, variants):
                common_json = json.loads(common)
                for item_variant in json.loads(variant):
                    yield self.item(common_json, item_variant)
        if response.json().get("has_next"):
            yield self.next_page()


class TodoEnPanalesSpider(TiendaNubeSpider):
    name = "todo_en_panales"
    allowed_domains = ["www.xn--todoenpaales-hhb.com.ar"]
    url = "https://www.xn--todoenpaales-hhb.com.ar/bebes/panales1"
    shipments = CABA

    def parse(self, response):
        """This function parses a sample response. Some contracts are mingled
        with this docstring.

        @url_custom https://www.xn--todoenpaales-hhb.com.ar/bebes/panales1/page/1/?results_only=true&limit=12 application/json
        @returns items 1 26
        @returns requests 0 1
        @scrapes description price url image website size units
        """
        return super().parse(response)


class PanalesOnlineSpider(TiendaNubeSpider):
    name = "panales_online"
    allowed_domains = ["www.panalesonline.com.ar"]
    url = "https://www.panalesonline.com.ar/panales/bebes"
    shipments = CABA + GBA

class PanaleraEnCasaSpider(TiendaNubeSpider):
    name = "panalera_en_casa"
    allowed_domains = ["www.lapanaleraencasa.com.ar"]
    url = "https://www.lapanaleraencasa.com.ar/bebe/panales"
    shipments = ROSARIO

class TiendalysSpider(TiendaNubeSpider):
    name = "tiendalys"
    allowed_domains = ["www.tiendalys.com.ar"]
    url = "https://www.tiendalys.com.ar/panales-de-bebe"
    shipments = CABA + GBA

class PanaleraMatluSpider(TiendaNubeSpider):
    name = "panalera_matlu"
    allowed_domains = ["www.panaleramatlu.com.ar"]
    url = "https://www.panaleramatlu.com.ar/panales-bebes"
    shipments = CABA + GBA

class PanaleraDoremiSpider(TiendaNubeSpider):
    name = "panalera_doremi"
    allowed_domains = ["www.panaleradoremi.com.ar"]
    url = "https://www.panaleradoremi.com.ar/panales/bebes"
    shipments = CABA

    def item(self, common, variant):
        return ScraperItem(
            description=common.get("name"),
            price=common.get("offers", {}).get("price"),
            url=common.get("offers", {}).get("url"),
            image=common.get("image"),
            website=self.allowed_domains[0],
            brand=None,
            size=None,
            units=None,
        )


class PanaleraEscondidaSpider(TiendaNubeSpider):
    name = "panalera_escondida"
    allowed_domains = ["www.xn--lapaaleraescondida-q0b.com.ar"]
    url = "https://www.xn--lapaaleraescondida-q0b.com.ar/panales-para-bebes"
    shipments = SANTA_CRUZ

    def item(self, common, variant):
        value = variant.get("option0")
        attrs = value.split(" x ") if value else []
        return ScraperItem(
            description=common.get("name"),
            price=variant.get("price_number"),
            url=common.get("offers", {}).get("url"),
            image=common.get("image"),
            website=self.allowed_domains[0],
            brand=None,
            size=attrs[0] if len(attrs) >= 1 else None,
            units=attrs[1] if len(attrs) >= 2 else None,
        )

class PanalOnceSpider(TiendaNubeSpider):
    name = "panal_once"
    allowed_domains = ["www.panalonce.com.ar"]
    url = "https://panalonce.com.ar/panales/bebes"
    shipments = CABA + GBA

# TODO: Los talles no se cargan via data-variants
#       tiene pinta que es tienda nube legacy como
#       noninoni.com.ar
class ParquePanalSpider(TiendaNubeSpider):
    name = "parque_panal"
    allowed_domains = ["www.parquepanial.com.ar"]
    url = "https://www.parquepanial.com.ar/panales-de-bebe"
    shipments = CABA

class AnaPerfumeriaSpider(TiendaNubeSpider):
    name = "ana_perfumeria"
    allowed_domains = ["www.anaperfumeriaonline.com.ar"]
    url = "https://www.anaperfumeriaonline.com.ar/panales/panales-bebe"
    shipments = ROSARIO

class PanolinoSpider(TiendaNubeSpider):
    name = "panolino"
    allowed_domains = ["www.panolino.com.ar"]
    url = "https://www.panolino.com.ar/bebes/oleos"
    shipments = CABA + GBA

    def item(self, common, variant):
        return ScraperItem(
            description=common.get("name"),
            price=common.get("offers", {}).get("price"),
            url=common.get("offers", {}).get("url"),
            image=common.get("image"),
            website=self.allowed_domains[0],
            brand=None,
            size=None,
            units=None,
        )

class VMComprasSpider(PanolinoSpider):
    name = "vmdecompras"
    allowed_domains = ["www.vmdecompras.com.ar"]
    url = "https://www.vmdecompras.com.ar/recien-nacido"
    shipments = SANTA_ROSA

class PerfumeriasMiriamSpider(TiendaNubeSpider):
    name = "perfumeriasmiriam"
    allowed_domains = ["www.perfumeriasmiriam.com.ar"]
    url = "https://www.perfumeriasmiriam.com/bebes-y-maternidad1/panales"
    shipments = CABA + GBA

    def item(self, common, variant):
        value = variant.get("option0")
        attrs = value.lower().replace(" x ", " ").split(" ") if value else []
        return ScraperItem(
            description=common.get("name"),
            price=variant.get("price_number"),
            url=common.get("offers", {}).get("url"),
            image=common.get("image"),
            website=self.allowed_domains[0],
            brand=None,
            size=attrs[0] if len(attrs) >= 1 else None,
            units=attrs[1] if len(attrs) >= 2 else None
        )

# TODO: Armar base TiendaNubeLegacy ya que no funciona con el
#       scraper actual.
#
class NoninoniSpider(TiendaNubeSpider):
    name = "noninoni"
    allowed_domains = ["www.noninoni.com.ar"]
    url = "https://www.noninoni.com.ar/panales/bebes"
    shipments = CABA + GBA

class MorashopSpider(TiendaNubeSpider):
    name = "morashop"
    allowed_domains = ["www.morashop.ar"]
    url = "https://www.morashop.ar/todo-para-tu-bebe/higiene-y-cuidado-del-bebe/panales"
    shipments = CABA

    def item(self, common, variant):
        size = f'{variant.get("option0")} {variant.get("option1")}'
        m = match(".*\((.*)\)", size)
        return ScraperItem(
            description=common.get("name"),
            price=variant.get("price_number"),
            url=common.get("offers", {}).get("url"),
            image=common.get("image"),
            website=self.allowed_domains[0],
            brand=None,
            size=m.group(1) if m else None,
            units=None,
        )


# TODO: Revisar porque muere en la pagina 2
class PiquilinesSpider(TiendaNubeSpider):
    name = "piquilines"
    allowed_domains = ["www.piquilines.com.ar"]
    url = "https://piquilines.com.ar/rn"
    shipments = SAN_JUAN

class TiendaMipanalSpider(TiendaNubeSpider):
    name = "tienda_mipanal"
    allowed_domains = ["www.xn--tiendamipaal-jhb.com.ar"]
    url = "https://www.xn--tiendamipaal-jhb.com.ar/panales"
    shipments = CABA + GBA