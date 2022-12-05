# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ToutiaoproItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    content = scrapy.Field()
    time = scrapy.Field()
    author = scrapy.Field()
    url = scrapy.Field()
    savePath = scrapy.Field()
    source = scrapy.Field()
    keyword = scrapy.Field()

