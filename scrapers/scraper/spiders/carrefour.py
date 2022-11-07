import base64
import json
import scrapy
from scraper.items import ScraperItem
from urllib.parse import urlencode


QUERY_ARGS = {
  "hideUnavailableItems": False,
  "skusFilter": "ALL_AVAILABLE",
  "simulationBehavior": "default",
  "installmentCriteria": "MAX_WITHOUT_INTEREST",
  "productOriginVtex": False,
  "map": "c,c",
  "query": "mundo-bebe/panales",
  "orderBy": "OrderByScoreDESC",
  "from": 64,
  "to": 79,
  "selectedFacets": [
    {
      "key": "c",
      "value": "mundo-bebe"
    },
    {
      "key": "c",
      "value": "panales"
    }
  ],
  "operator": "and",
  "fuzzy": "0",
  "searchState": None,
  "facetsBehavior": "Static",
  "categoryTreeBehavior": "default",
  "withFacets": False
}

class CarrefourSpider(scrapy.Spider):
    name = 'carrefour'
    allowed_domains = ['www.carrefour.com.ar']
    start_urls = ['https://www.carrefour.com.ar/_v/segment/graphql/v1']
    page_size = 15

    def __init__(self, *args, **kwargs):
        super(CarrefourSpider, self).__init__(*args, **kwargs)
        self._current_page = 0

    def _prepare_page(self, curr_page, next_page):
        query_args = QUERY_ARGS.copy()
        query_args['from'] = curr_page * self.page_size
        query_args['to'] = next_page * self.page_size
        json_query_args = json.dumps(query_args)
        return base64.b64encode(json_query_args.encode()).decode()

    def next_page(self):
        url = self.start_urls[0]
        enconded_params = self._prepare_page(self._current_page, self._current_page+1)
        extensions = '{"persistedQuery":{"version":1,"sha256Hash":"67d0a6ef4d455f259737e4edb1ed58f6db9ff823570356ebc88ae7c5532c0866","sender":"vtex.store-resources@0.x","provider":"vtex.search-graphql@0.x"},"variables":"'+ enconded_params +'"}'
        querystring = {
            "workspace": "master",
            "maxAge": "short",
            "appsEtag": "remove",
            "domain":"store",
            "locale":"es-AR",
            "__bindingId":"ecd0c46c-3b2a-4fe1-aae0-6080b7240f9b",
            "operationName": "productSearchV3",
            "variables": "{}",
            "extensions": extensions,
        }
        url = url + '?' + urlencode(querystring)
        request = scrapy.Request(url, method="GET")
        self._current_page += 1
        return request

    def start_requests(self):
        yield self.next_page()

    def parse(self, response):
        """This function parses a sample response. Some contracts are mingled
        with this docstring.

        @url https://www.carrefour.com.ar/_v/segment/graphql/v1?workspace=master&maxAge=short&appsEtag=remove&domain=store&locale=es-AR&__bindingId=ecd0c46c-3b2a-4fe1-aae0-6080b7240f9b&operationName=productSearchV3&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%2267d0a6ef4d455f259737e4edb1ed58f6db9ff823570356ebc88ae7c5532c0866%22%2C%22sender%22%3A%22vtex.store-resources%400.x%22%2C%22provider%22%3A%22vtex.search-graphql%400.x%22%7D%2C%22variables%22%3A%22eyJoaWRlVW5hdmFpbGFibGVJdGVtcyI6IGZhbHNlLCAic2t1c0ZpbHRlciI6ICJBTExfQVZBSUxBQkxFIiwgInNpbXVsYXRpb25CZWhhdmlvciI6ICJkZWZhdWx0IiwgImluc3RhbGxtZW50Q3JpdGVyaWEiOiAiTUFYX1dJVEhPVVRfSU5URVJFU1QiLCAicHJvZHVjdE9yaWdpblZ0ZXgiOiBmYWxzZSwgIm1hcCI6ICJjLGMiLCAicXVlcnkiOiAibXVuZG8tYmViZS9wYW5hbGVzIiwgIm9yZGVyQnkiOiAiT3JkZXJCeVNjb3JlREVTQyIsICJmcm9tIjogMTA1LCAidG8iOiAxMjAsICJzZWxlY3RlZEZhY2V0cyI6IFt7ImtleSI6ICJjIiwgInZhbHVlIjogIm11bmRvLWJlYmUifSwgeyJrZXkiOiAiYyIsICJ2YWx1ZSI6ICJwYW5hbGVzIn1dLCAib3BlcmF0b3IiOiAiYW5kIiwgImZ1enp5IjogIjAiLCAic2VhcmNoU3RhdGUiOiBudWxsLCAiZmFjZXRzQmVoYXZpb3IiOiAiU3RhdGljIiwgImNhdGVnb3J5VHJlZUJlaGF2aW9yIjogImRlZmF1bHQiLCAid2l0aEZhY2V0cyI6IGZhbHNlfQ%3D%3D%22%7D
        @returns items 1 15
        @returns requests 0 1
        @scrapes description price url image website
        """
        items = response.json().get("data", {}).get("productSearch", {}).get("products", [])
        for item in items:
            price = item.get("priceRange", {}).get("sellingPrice", {}).get("highPrice")
            image = item.get("items", [{"images": [{"imageUrl": None}]}])[0].get("images", [{"imageUrl": None}])[0].get("imageUrl")
            url = self.allowed_domains[0] + item.get("link")
            description = item.get("productName")
            brand = item.get("brand")
            yield ScraperItem(
                description=description,
                price=price,
                url=url,
                image=image,
                website=self.allowed_domains[0],
                brand=brand,
            )
        if items:
            yield self.next_page()

