# -*- coding: utf-8 -*-
# Источник https://auto.youla.ru/
#
# Обойти все марки авто и зайти на странички объявлений
# Собрать след стуркутру и сохранить в БД Монго
#
# Название объявления
# Список фото объявления (ссылки)
# Список характеристик
# Описание объявления
# ссылка на автора объявления
# дополнительно попробуйте вытащить телефона


import scrapy

from furl import furl
from pymongo import MongoClient
from datetime import datetime


class YolaRuSpider(scrapy.Spider):
    name = 'yola_ru'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    datepoint = datetime.today().strftime('%Y%m%d')

    xpath = {
        'get_brand': '//div[contains(@class, "TransportMainFilters_brandsList")]//a[@class="blackLink"]/@href',
        'paginator': '//div[contains(@class, "Paginator_total")]/text()[2]',
        'page_car': '//div[contains(@class, "SerpSnippet_snippetContent")]//a[@class="SerpSnippet_photoWrapper__3W9J4"]/@href',
        'parse_head': '//div[contains(@class, "AdvertCard_advertTitle")]/text()',
        'parse_photo': '//div[contains(@class, "PhotoGallery_block")]//img/@src',

    }
    car_specifications = {
        'year': lambda response: response.xpath(
            '//div[contains(@class, "AdvertSpecs_data") and @data-target="advert-info-year"]/a[@class="blackLink"]/text()').extract_first(),
        'odometr': lambda response: response.xpath(
            '//div[contains(@class, "AdvertSpecs_data") and @data-target="advert-info-mileage"]/text()').extract_first(),
        'corpus': lambda response: response.xpath(
            '//div[contains(@class, "AdvertSpecs_data") and @data-target="advert-info-bodyType"]/a[@class="blackLink"]/text()').extract_first(),
        'kpp': lambda response: response.xpath(
            '//div[contains(@class, "AdvertSpecs_data") and @data-target="advert-info-transmission"]/text()').extract_first(),
        'engine': lambda response: response.xpath(
            '//div[contains(@class, "AdvertSpecs_data") and @data-target="advert-info-engineInfo"]/text()').extract_first(),
        'wheel': lambda response: response.xpath(
            '//div[contains(@class, "AdvertSpecs_data") and @data-target="advert-info-wheelType"]/text()').extract_first(),
        'color': lambda response: response.xpath(
            '//div[contains(@class, "AdvertSpecs_data") and @data-target="advert-info-color"]/text()').extract_first(),
        'transmission': lambda response: response.xpath(
            '//div[contains(@class, "AdvertSpecs_data") and @data-target="advert-info-driveType"]/text()').extract_first(),
        'power': lambda response: response.xpath(
            '//div[contains(@class, "AdvertSpecs_data") and @data-target="advert-info-enginePower"]/text()').extract_first(),
        'customs': lambda response: response.xpath(
            '//div[contains(@class, "AdvertSpecs_data") and @data-target="advert-info-isCustom"]/text()').extract_first(),
        'owners': lambda response: response.xpath(
            '//div[contains(@class, "AdvertSpecs_data") and @data-target="advert-info-owners"]/text()').extract_first(),

        'description': lambda response: response.xpath(
            '//div[contains(@class, "AdvertCard_descriptionInner") and @data-target="advert-info-descriptionFull"]/text()').extract_first(),
        # 'seller_link': '',

    }

    def __init__(self):
        mongo_connect = MongoClient('mongodb://localhost:27017')
        self.mongodb = mongo_connect['youla']

    def parse(self, response, **kwargs):
        for url in response.xpath(self.xpath['get_brand']):
            yield response.follow(url=url, callback=self.brand_pagination_parse)

    def brand_pagination_parse(self, response, **kwargs):
        # Пагинатор
        try:
            page_count = int(response.xpath(self.xpath['paginator']).extract()[0])
        except Exception as ex:

            page_count = 1

        print(f'Page count: {page_count}')
        while page_count:
            page_url = furl(response.url).add({'page': page_count})
            yield response.follow(page_url.url, callback=self.brand_parse)
            page_count = page_count - 1

    def brand_parse(self, response, **kwargs):
        for url_car in response.xpath(self.xpath['page_car']):
            yield response.follow(url=url_car, callback=self.car_parse)

    def car_parse(self, response, **kwargs):
        data = {
            'head': response.xpath(self.xpath['parse_head']).extract_first(),
            'list_of_photo': response.xpath(self.xpath['parse_photo']).extract(),
        }
        for specification, val in self.car_specifications.items():
            try:
                data[specification] = val(response)
            except Exception as ex:
                data[specification] = ex
        print(data)
        collection = self.mongodb['youla_' + self.datepoint]
        collection.insert_one(data)
        print(data)
