import scrapy
import datetime
import requests


from ..loaders import HhAutoLoader, HhEmployerAutoLoader


# Источник https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113
# вакансии удаленной работы.
#
# Задача: Обойти с точки входа все вакансии и собрать след данные:
#
# название вакансии
# оклад (строкой от до или просто сумма)
# Описание вакансии
# ключевые навыки - в виде списка названий
# ссылка на автора вакансии

# Перейти на страницу автора вакансии,
# собрать данные:
# Название
# сайт ссылка (если есть)
# сферы деятельности (списком)
# Описание
# Обойти и собрать все вакансии данного автора.
#
# Обязательно использовать Loader Items Pipelines


class HhruSpider(scrapy.Spider):
    name = 'hhRu'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113&page=0']

    datepoint = datetime.datetime.today().strftime('%Y%m%d')

    xpath = {
        'ad_link': '//div[contains(@class, "vacancy-serp-item__info")]//a[@class="bloko-link HH-LinkModifier"]/@href',
        'paginator': '//div[contains(@class, "bloko-gap bloko-gap_top")]//a[contains(@class, "HH-Pager-Controls-Next")]/@href',

        'title': '//div[@class="vacancy-title"]/h1[@data-qa="vacancy-title"]/text()',
        'salary': '//p[@class="vacancy-salary"]/span/text()',
        'description': '//div[@data-qa="vacancy-description"]/p//text()',
        'vacancy_tags': '//div[@class="vacancy-section"]/div[@class="bloko-tag-list"]//text()',
        'autor_link': '//div[@class="vacancy-company-wrapper"]//a/@href',

        'comp_name': '//div[@class="company-header"]//span[@class="company-header-title-name"]//text()',
        'comp_site': '//div[@class="employer-sidebar-content"]//a[@class="g-user-content"]/@href/text()',
        'comp_desc': '//div[@class="company-description"]//p/text()',
        'comp_job_openings': '//div//a[@data-qa="vacancy-serp__vacancy-title"]/@href'


    }

    def parse(self, response, **kwargs):

        #Ходим по объявлениям
        for url in response.xpath(self.xpath['ad_link']).extract():
            yield response.follow(url, callback=self.parse_ad)

        #Ходим по страницам
        yield response.follow(response.xpath(self.xpath['paginator']).extract_first(), callback=self.parse)

    def parse_ad(self, response, **kwargs):
        #Готовим респонс работодателя
        url = f"https://korolev.hh.ru{response.xpath(self.xpath['autor_link']).extract_first()}"

        loader = HhAutoLoader(response=response)
        loader.add_xpath('title' , self.xpath['title'])
        loader.add_xpath('salary', self.xpath['salary'])
        loader.add_xpath('description', self.xpath['description'])
        loader.add_xpath('vacancy_tags', self.xpath['vacancy_tags'])
        loader.add_xpath('autor_link', self.xpath['autor_link'])
        #
        # #Переходим на ссылку работодателя
        loader.add_value('url', response.url)

        yield loader.load_item()
        yield response.follow(url, callback=self.company_parse, cb_kwargs={'loader': loader})

    def company_parse(self, response, **kwargs):
        loader = HhEmployerAutoLoader(response=response)
        loader.add_value('url', response.url)
        loader.add_xpath('comp_name', self.xpath['comp_name'])
        loader.add_xpath('comp_site', self.xpath['comp_site'])
        loader.add_xpath('comp_desc', self.xpath['comp_desc'])

        yield loader.load_item()
        #
        for url in response.xpath(self.xpath['comp_job_openings']):
            yield response.follow(url, callback=self.parse_ad)
