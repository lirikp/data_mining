from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from hhpars import settings
from hhpars.spiders.hhRu import HhruSpider

if __name__ == '__main__':
    crowl_settings = Settings()
    crowl_settings.setmodule(settings)
    crowl_proc = CrawlerProcess(settings=crowl_settings)

    crowl_proc.crawl(HhruSpider)
    crowl_proc.start()