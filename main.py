from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from yola_ru_parse import settings
from yola_ru_parse.spiders.yola_ru import YolaRuSpider

if __name__ == '__main__':
    crowl_settings = Settings()
    crowl_settings.setmodule(settings)
    crowl_proc = CrawlerProcess(settings=crowl_settings)

    crowl_proc.crawl(YolaRuSpider)
    crowl_proc.start()