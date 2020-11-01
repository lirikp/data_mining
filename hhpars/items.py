# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HhparsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()
    vacancy_tags = scrapy.Field()
    autor_link = scrapy.Field()
    comp_name = scrapy.Field()
    comp_site = scrapy.Field()
    comp_desc = scrapy.Field()

class HhEmployerparsItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    comp_name = scrapy.Field()
    comp_site = scrapy.Field()
    comp_desc = scrapy.Field()
