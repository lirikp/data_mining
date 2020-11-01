import re
from scrapy import Selector
from itemloaders.processors import TakeFirst, MapCompose
from scrapy.loader import ItemLoader

from .items import HhparsItem, HhEmployerparsItem

def create_employer_url(itm):
    base_url = "https://korolev.hh.ru"
    result = base_url + itm
    return result

def vacancy_tags(itm):
    return '|'.join(itm)


class HhAutoLoader(ItemLoader):
    default_item_class = HhparsItem
    autor_link_in = MapCompose(create_employer_url)
    description_in = ''.join
    salary_in = ''.join
    vacancy_tags_in = vacancy_tags

    url_out = TakeFirst()

    salary_out = TakeFirst()
    title_out = TakeFirst()
    description_out = TakeFirst()
    vacancy_tags_out = TakeFirst()
    autor_link_out = TakeFirst()

class HhEmployerAutoLoader(ItemLoader):
    default_item_class = HhEmployerparsItem

    url_out = TakeFirst()
    comp_name_out = TakeFirst()
    comp_site_out = TakeFirst()
    comp_desc_out = TakeFirst()

