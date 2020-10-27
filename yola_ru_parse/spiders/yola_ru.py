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

class YolaRuSpider(scrapy.Spider):
    name = 'yola_ru'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    def parse(self, response, **kwargs): #land_rover
        for url in response.xpath(
                '//div[@class="TransportMainFilters_brandsList__2tIkv"]//a[@class="blackLink"]/@href'):
            yield response.follow(url=url, callback=self.brand_pagination_parse)

    def brand_pagination_parse(self, response, **kwargs):
        #Пагинатор
        try:
            page_count = int(response.xpath('//div[@class="Paginator_total__oFW1n"]/text()[2]').extract()[0])
        except Exception as ex:

            page_count = 1

        print(f'Page count: {page_count}')
        while page_count:
            page_url = furl(response.url).add({'page': page_count})
            yield response.follow(page_url.url, callback=self.brand_parse)
            page_count = page_count-1

    def brand_parse(self, response, **kwargs):
        for url_car in response.xpath('//div[@class="SerpSnippet_snippetContent__d8CHK"]//a[@class="SerpSnippet_photoWrapper__3W9J4"]/@href'):
           yield response.follow(url=url_car, callback=self.car_parse)

    def car_parse(self,response, **kwargs):
        data = {
            'head': response.xpath('//div[@class="AdvertCard_advertTitle__1S1Ak"]/text()').extract()[0],
            'list_of_photo': response.xpath('//div[@class="FullscreenGallery_whiteBorder__3nNFN"]'),
        }
        print(data)

