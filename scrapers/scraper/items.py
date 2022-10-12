# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScraperItem(scrapy.Item):
    description = scrapy.Field()
    price = scrapy.Field()
    url = scrapy.Field()
    image = scrapy.Field()
    website = scrapy.Field()
