from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable, List, Optional, Sequence, Set, Union


AVAILABLE = "available"
UNAVAILABLE = "unavailable"
NEEDS_REVIEW = "needs_review"

SCRAPER_IMPLEMENTED = "implemented"
SCRAPER_CANDIDATE = "candidate"
SCRAPER_NEEDS_REVIEW = "needs_review"

CHECKED_AT = "2026-08-24T19:25:00-03:00"


@dataclass(frozen=True)
class StoreSource:
    id: str
    name: str
    diaper_url: str
    status: str
    scraper_status: str
    homepage_url: Optional[str] = None
    canonical_url: Optional[str] = None
    spider: Optional[str] = None
    ecommerce: Optional[str] = None
    http_status: Optional[int] = None
    checked_at: str = CHECKED_AT
    regions: Sequence[str] = ()
    popular_buenos_aires: bool = False
    notes: Optional[str] = None


SOURCE_STORES: Sequence[StoreSource] = (
    StoreSource(
        id="panales_online",
        name="La Panalera / Panales Online",
        homepage_url="https://www.panalesonline.com.ar/",
        diaper_url="https://www.panalesonline.com.ar/panales/bebes/",
        canonical_url="https://www.panalesonline.com.ar/panales/bebes/",
        status=AVAILABLE,
        http_status=200,
        scraper_status=SCRAPER_IMPLEMENTED,
        spider="panales_online",
        ecommerce="tienda_nube",
        regions=("caba", "gba", "amba"),
        popular_buenos_aires=True,
    ),
    StoreSource(
        id="mundo_panal",
        name="El Mundo del Panal",
        homepage_url="https://xn--elmundodelpaal-1nb.com.ar/",
        diaper_url="https://xn--elmundodelpaal-1nb.com.ar/#!/categoria/33/pagina/0/",
        canonical_url="https://xn--elmundodelpaal-1nb.com.ar/",
        status=AVAILABLE,
        http_status=200,
        scraper_status=SCRAPER_IMPLEMENTED,
        spider="mundo_panal",
        ecommerce="custom",
    ),
    StoreSource(
        id="panalera_delta",
        name="Panalera Delta",
        homepage_url="https://panaleradelta.com.ar/",
        diaper_url="https://panaleradelta.com.ar/product-category/panales-de-bebes/",
        canonical_url="https://panaleradelta.com.ar/product-category/panales-de-bebes/",
        status=AVAILABLE,
        http_status=200,
        scraper_status=SCRAPER_IMPLEMENTED,
        spider="panalera_delta",
        ecommerce="woocommerce",
    ),
    StoreSource(
        id="todo_en_panales",
        name="Todo en Panales",
        homepage_url="https://xn--todoenpaales-hhb.com.ar/",
        diaper_url="https://www.xn--todoenpaales-hhb.com.ar/bebes/panales1/",
        canonical_url="https://xn--todoenpaales-hhb.com.ar/bebes/panales1/",
        status=AVAILABLE,
        http_status=200,
        scraper_status=SCRAPER_IMPLEMENTED,
        spider="todo_en_panales",
        ecommerce="tienda_nube",
        regions=("caba",),
    ),
    StoreSource(
        id="panalera_en_casa",
        name="La Panalera en Casa",
        homepage_url="https://lapanaleraencasa.com.ar/",
        diaper_url="https://www.lapanaleraencasa.com.ar/bebe/panales",
        canonical_url="https://lapanaleraencasa.com.ar/bebe/panales",
        status=AVAILABLE,
        http_status=200,
        scraper_status=SCRAPER_IMPLEMENTED,
        spider="panalera_en_casa",
        ecommerce="tienda_nube",
        regions=("rosario",),
    ),
    StoreSource(
        id="tiendalys",
        name="Tienda L&S",
        homepage_url="https://www.tiendalys.com.ar/",
        diaper_url="https://www.tiendalys.com.ar/panales-de-bebe/",
        canonical_url="https://www.tiendalys.com.ar/panales-de-bebe/",
        status=AVAILABLE,
        http_status=200,
        scraper_status=SCRAPER_IMPLEMENTED,
        spider="tiendalys",
        ecommerce="tienda_nube",
        regions=("caba", "gba", "amba"),
    ),
    StoreSource(
        id="panalera_todo_en_panales_mercadoshops",
        name="Panalera Todo en Panales MercadoShops",
        diaper_url="https://paaleratodoenpaales.mercadoshops.com.ar/listado/bebes/",
        status=UNAVAILABLE,
        scraper_status=SCRAPER_NEEDS_REVIEW,
        ecommerce="mercado_shops",
        regions=("caba",),
        notes="DNS lookup failed for the listed MercadoShops host.",
    ),
    StoreSource(
        id="panalera_matlu",
        name="Panalera Matlu",
        homepage_url="https://www.panaleramatlu.com.ar/",
        diaper_url="https://www.panaleramatlu.com.ar/panales-bebes/",
        status=UNAVAILABLE,
        scraper_status=SCRAPER_NEEDS_REVIEW,
        spider="panalera_matlu",
        ecommerce="tienda_nube",
        regions=("caba", "gba", "amba"),
        notes="DNS lookup failed for the configured domain.",
    ),
    StoreSource(
        id="panalera_doremi",
        name="Panalera DO RE MI",
        homepage_url="https://www.panaleradoremi.com.ar/",
        diaper_url="https://www.panaleradoremi.com.ar/panales/bebes/",
        canonical_url="https://www.panaleradoremi.com.ar/panales/bebes/",
        status=AVAILABLE,
        http_status=200,
        scraper_status=SCRAPER_IMPLEMENTED,
        spider="panalera_doremi",
        ecommerce="tienda_nube",
        regions=("caba",),
    ),
    StoreSource(
        id="travesurasonline",
        name="Travesuras Online",
        homepage_url="https://travesurasonline.sed.com.ar/",
        diaper_url="https://travesurasonline.sed.com.ar/catalogo;r=pa%C3%B1al%20bebe;s=pa%C3%B1al%20bebe;clear=true",
        canonical_url="https://travesurasonline.sed.com.ar/catalogo;r=pa%C3%B1al%20bebe;s=pa%C3%B1al%20bebe;clear=true",
        status=AVAILABLE,
        http_status=200,
        scraper_status=SCRAPER_IMPLEMENTED,
        spider="travesurasonline",
        ecommerce="sed",
    ),
    StoreSource(
        id="panalera_escondida",
        name="La Panalera Escondida",
        homepage_url="https://www.xn--lapaaleraescondida-q0b.com.ar/",
        diaper_url="https://www.xn--lapaaleraescondida-q0b.com.ar/panales-para-bebes/",
        canonical_url="https://www.xn--lapaaleraescondida-q0b.com.ar/panales-para-bebes/",
        status=AVAILABLE,
        http_status=200,
        scraper_status=SCRAPER_IMPLEMENTED,
        spider="panalera_escondida",
        ecommerce="tienda_nube",
        regions=("santa_cruz",),
    ),
    StoreSource(
        id="cotodigital",
        name="Coto Digital",
        homepage_url="https://www.coto.com.ar/",
        diaper_url="https://www.cotodigital3.com.ar/sitios/cdigi/browse/catalogo-perfumer%C3%ADa-pa%C3%B1ales-y-productos-para-incontinencia-pa%C3%B1ales-para-beb%C3%A9/_/N-fmf3uu",
        canonical_url="https://www.coto.com.ar/browse/catalogo-perfumer%C3%ADa-pa%C3%B1ales-y-productos-para-incontinencia-pa%C3%B1ales-para-beb%C3%A9/_/N-fmf3uu",
        status=AVAILABLE,
        http_status=200,
        scraper_status=SCRAPER_IMPLEMENTED,
        spider="cotodigital",
        ecommerce="custom",
        regions=("caba", "gba", "amba"),
        popular_buenos_aires=True,
        notes="Old cotodigital3 URL redirects to www.coto.com.ar.",
    ),
    StoreSource(
        id="jumbo",
        name="Jumbo",
        homepage_url="https://www.jumbo.com.ar/",
        diaper_url="https://www.jumbo.com.ar/bebes-y-ninos/panales",
        canonical_url="https://www.jumbo.com.ar/mundo-bebe/panales",
        status=AVAILABLE,
        http_status=200,
        scraper_status=SCRAPER_IMPLEMENTED,
        spider="jumbo",
        ecommerce="vtex",
        regions=("caba", "gba", "amba"),
        popular_buenos_aires=True,
        notes="Old /bebes-y-ninos/panales path redirects to /mundo-bebe/panales.",
    ),
    StoreSource(
        id="carrefour",
        name="Carrefour",
        homepage_url="https://www.carrefour.com.ar/",
        diaper_url="https://www.carrefour.com.ar/mundo-bebe/panales",
        canonical_url="https://www.carrefour.com.ar/mundo-bebe/panales",
        status=AVAILABLE,
        http_status=200,
        scraper_status=SCRAPER_IMPLEMENTED,
        spider="carrefour",
        ecommerce="vtex",
        regions=("caba", "gba", "amba"),
        popular_buenos_aires=True,
    ),
    StoreSource(
        id="meli",
        name="Mercado Libre",
        homepage_url="https://www.mercadolibre.com.ar/",
        diaper_url="https://listado.mercadolibre.com.ar/panalera",
        canonical_url="https://listado.mercadolibre.com.ar/panalera",
        status=AVAILABLE,
        scraper_status=SCRAPER_NEEDS_REVIEW,
        spider="meli",
        ecommerce="mercado_libre",
        regions=("argentina",),
        notes="Spider remains excluded from all because it needs an API-safe integration.",
    ),
    StoreSource(
        id="panal_once",
        name="Panal Once",
        homepage_url="https://panalonce.com.ar/",
        diaper_url="https://panalonce.com.ar/panales/bebes",
        canonical_url="https://panalonce.com.ar/panales/bebes",
        status=AVAILABLE,
        http_status=200,
        scraper_status=SCRAPER_IMPLEMENTED,
        spider="panal_once",
        ecommerce="tienda_nube",
        regions=("caba", "gba", "amba"),
        popular_buenos_aires=True,
    ),
    StoreSource(
        id="parque_panal",
        name="Parque Panal",
        homepage_url="https://www.parquepanial.com.ar/",
        diaper_url="https://www.parquepanial.com.ar/panales-de-bebe",
        canonical_url="https://www.parquepanial.com.ar/panales-de-bebe",
        status=AVAILABLE,
        http_status=200,
        scraper_status=SCRAPER_NEEDS_REVIEW,
        spider="parque_panal",
        ecommerce="tienda_nube",
        regions=("caba",),
        notes="Reachable, but the existing spider is marked legacy/TODO.",
    ),
    StoreSource(
        id="ana_perfumeria",
        name="Ana Perfumeria",
        homepage_url="https://www.anaperfumeriaonline.com.ar/",
        diaper_url="https://www.anaperfumeriaonline.com.ar/panales/panales-bebe",
        status=UNAVAILABLE,
        scraper_status=SCRAPER_NEEDS_REVIEW,
        spider="ana_perfumeria",
        ecommerce="tienda_nube",
        regions=("rosario",),
        notes="DNS lookup failed for the configured domain.",
    ),
    StoreSource(
        id="panolino",
        name="Panolino",
        homepage_url="https://www.panolino.com.ar/",
        diaper_url="https://www.panolino.com.ar/bebes/oleos",
        canonical_url="https://www.panolino.com.ar/bebes/oleos",
        status=NEEDS_REVIEW,
        http_status=200,
        scraper_status=SCRAPER_NEEDS_REVIEW,
        spider="panolino",
        ecommerce="tienda_nube",
        regions=("caba", "gba", "amba"),
        notes="The configured URL is live but points to oleos, not a diaper category.",
    ),
    StoreSource(
        id="vmdecompras",
        name="VM de Compras",
        homepage_url="https://www.vmdecompras.com.ar/",
        diaper_url="https://www.vmdecompras.com.ar/recien-nacido",
        status=UNAVAILABLE,
        scraper_status=SCRAPER_NEEDS_REVIEW,
        spider="vmdecompras",
        ecommerce="tienda_nube",
        regions=("santa_rosa",),
        notes="DNS lookup failed for the configured domain.",
    ),
    StoreSource(
        id="perfumeriasmiriam",
        name="Perfumerias Miriam",
        homepage_url="https://www.perfumeriasmiriam.com/",
        diaper_url="https://www.perfumeriasmiriam.com/bebes-y-maternidad1/panales",
        canonical_url="https://www.perfumeriasmiriam.com/bebes-y-maternidad1/panales",
        status=NEEDS_REVIEW,
        http_status=200,
        scraper_status=SCRAPER_NEEDS_REVIEW,
        spider="perfumeriasmiriam",
        ecommerce="tienda_nube",
        regions=("caba", "gba", "amba"),
        notes="Live URL uses .com while the spider allowed domain is .com.ar.",
    ),
    StoreSource(
        id="noninoni",
        name="Noninoni",
        homepage_url="https://noninoni.com.ar/",
        diaper_url="https://www.noninoni.com.ar/panales/bebes",
        canonical_url="https://noninoni.com.ar/panales/bebes",
        status=UNAVAILABLE,
        http_status=404,
        scraper_status=SCRAPER_NEEDS_REVIEW,
        spider="noninoni",
        ecommerce="wordpress",
        regions=("caba", "gba", "amba"),
        notes="The configured diaper path redirects to a 404.",
    ),
    StoreSource(
        id="morashop",
        name="Morashop",
        homepage_url="https://www.morashop.ar/",
        diaper_url="https://www.morashop.ar/todo-para-tu-bebe/higiene-y-cuidado-del-bebe/panales",
        status=UNAVAILABLE,
        http_status=404,
        scraper_status=SCRAPER_NEEDS_REVIEW,
        spider="morashop",
        ecommerce="tienda_nube",
        regions=("caba",),
        notes="The configured diaper path returns 404.",
    ),
    StoreSource(
        id="piquilines",
        name="Piquilines",
        homepage_url="https://piquilines.com.ar/",
        diaper_url="https://piquilines.com.ar/rn",
        status=UNAVAILABLE,
        scraper_status=SCRAPER_NEEDS_REVIEW,
        spider="piquilines",
        ecommerce="tienda_nube",
        regions=("san_juan",),
        notes="DNS lookup failed for the configured domain.",
    ),
    StoreSource(
        id="tienda_mipanal",
        name="Tienda Mi Panal",
        homepage_url="https://www.xn--tiendamipaal-jhb.com.ar/",
        diaper_url="https://www.xn--tiendamipaal-jhb.com.ar/panales",
        status=UNAVAILABLE,
        http_status=404,
        scraper_status=SCRAPER_NEEDS_REVIEW,
        spider="tienda_mipanal",
        ecommerce="tienda_nube",
        regions=("caba", "gba", "amba"),
        notes="The configured diaper path returns 404.",
    ),
    StoreSource(
        id="dia",
        name="Dia Online",
        homepage_url="https://diaonline.supermercadosdia.com.ar/",
        diaper_url="https://diaonline.supermercadosdia.com.ar/bebes-y-ninos/panales/panales/babysec?map=category-1%2Ccategory-2%2Ccategory-3%2Cbrand",
        canonical_url="https://diaonline.supermercadosdia.com.ar/bebes-y-ninos/panales/panales/babysec?map=category-1%2Ccategory-2%2Ccategory-3%2Cbrand",
        status=AVAILABLE,
        http_status=200,
        scraper_status=SCRAPER_CANDIDATE,
        ecommerce="vtex",
        regions=("caba", "gba", "amba"),
        popular_buenos_aires=True,
        notes="Popular AMBA source from the live comparison set; spider not implemented yet.",
    ),
    StoreSource(
        id="farmacity",
        name="Farmacity",
        homepage_url="https://www.farmacity.com/",
        diaper_url="https://www.farmacity.com/panales/bebes?map=ft",
        canonical_url="https://www.farmacity.com/panales/bebes?map=ft",
        status=AVAILABLE,
        http_status=200,
        scraper_status=SCRAPER_CANDIDATE,
        ecommerce="vtex",
        regions=("caba", "gba", "amba"),
        popular_buenos_aires=True,
        notes="Popular AMBA pharmacy source; spider not implemented yet.",
    ),
    StoreSource(
        id="disco",
        name="Disco",
        homepage_url="https://www.disco.com.ar/",
        diaper_url="https://www.disco.com.ar/mundo-bebe/panales",
        canonical_url="https://www.disco.com.ar/mundo-bebe/panales",
        status=AVAILABLE,
        http_status=200,
        scraper_status=SCRAPER_CANDIDATE,
        ecommerce="vtex",
        regions=("caba", "gba", "amba"),
        popular_buenos_aires=True,
        notes="Popular AMBA supermarket source; spider not implemented yet.",
    ),
    StoreSource(
        id="vea",
        name="Vea",
        homepage_url="https://www.vea.com.ar/",
        diaper_url="https://www.vea.com.ar/mundo-bebe/panales",
        canonical_url="https://www.vea.com.ar/mundo-bebe/panales",
        status=AVAILABLE,
        http_status=200,
        scraper_status=SCRAPER_CANDIDATE,
        ecommerce="vtex",
        regions=("caba", "gba", "amba"),
        popular_buenos_aires=True,
        notes="Popular AMBA supermarket source; spider not implemented yet.",
    ),
    StoreSource(
        id="panalera_babybear",
        name="Panalera Baby Bear",
        homepage_url="https://www.panalerababybear.com.ar/",
        diaper_url="https://www.panalerababybear.com.ar/productos/",
        canonical_url="https://www.panalerababybear.com.ar/",
        status=AVAILABLE,
        http_status=200,
        scraper_status=SCRAPER_CANDIDATE,
        ecommerce="tienda_nube",
        regions=("caba", "gba", "amba"),
        popular_buenos_aires=True,
        notes="Local Buenos Aires Tienda Nube store with diaper products; spider not implemented yet.",
    ),
    StoreSource(
        id="tienda_juma",
        name="Tienda Juma",
        homepage_url="https://tiendajuma.com.ar/",
        diaper_url="https://tiendajuma.com.ar/",
        canonical_url="https://tiendajuma.com.ar/",
        status=AVAILABLE,
        http_status=200,
        scraper_status=SCRAPER_CANDIDATE,
        ecommerce="woocommerce",
        regions=("caba", "gba", "amba"),
        popular_buenos_aires=True,
        notes="Local Buenos Aires diaper store; spider not implemented yet.",
    ),
)


FilterValues = Union[Iterable[str], str]


def _normalize_values(values: Optional[FilterValues]) -> Set[str]:
    if values is None:
        return set()
    if isinstance(values, str):
        values = values.split(",")
    return {str(value).strip().lower() for value in values if str(value).strip()}


def source_to_dict(source: StoreSource) -> dict:
    item = asdict(source)
    item["regions"] = list(source.regions)
    return item


def list_source_stores(
    availability: Optional[FilterValues] = None,
    region: Optional[str] = None,
    scraper_status: Optional[FilterValues] = None,
    popular_buenos_aires: Optional[bool] = None,
) -> List[dict]:
    statuses = _normalize_values(availability)
    scraper_statuses = _normalize_values(scraper_status)
    region_value = (region or "").strip().lower()
    rows = []
    for source in SOURCE_STORES:
        if statuses and source.status.lower() not in statuses:
            continue
        if scraper_statuses and source.scraper_status.lower() not in scraper_statuses:
            continue
        if region_value and region_value not in {value.lower() for value in source.regions}:
            continue
        if popular_buenos_aires is not None and source.popular_buenos_aires != popular_buenos_aires:
            continue
        rows.append(source_to_dict(source))
    return rows


def implemented_active_spiders(available_spiders: Iterable[str]) -> List[str]:
    available = set(available_spiders)
    by_spider = {source.spider: source for source in SOURCE_STORES if source.spider}
    selected = []
    for spider in sorted(available):
        source = by_spider.get(spider)
        if source is None:
            selected.append(spider)
            continue
        if source.status == AVAILABLE and source.scraper_status == SCRAPER_IMPLEMENTED:
            selected.append(spider)
    return selected
