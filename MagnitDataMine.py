import requests
import http.client
import datetime

from urllib.parse import urlparse
from pymongo import MongoClient
from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_date


class magnitDataMinePromo():
    _params = {'geo': '', }
    _date_point = datetime.datetime.today().strftime('%Y%m%d_%H')

    http.client._MAXHEADERS = 1000

    __headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
    }

    product_template = {
        # 'url': '',  # ссылка на товар
        'promo_name': ('div', 'action__name', 'text'),  # Название акции
        'product_name': ('div', 'action__title', 'text'),  # Название продукта
        'old_price': ('div', 'label__price_old', 'text'),  # стоимость старая(Тип Float)
        'new_price': ('div', 'label__price_new', 'text'),  # стоимсоть новая(Тип Float)
        'image_url': ('div', 'col-2 col-t-5 action__col action__col_img', 'data-src'),  # ссылка на изображение
        'date_from': ('div', 'action__date-label',),  # дата начала акции(тип datetime)
        'date_to': ('div', 'action__date-label',),  # дата окончания(тип datetime)
    }

    def __init__(self, url):
        self.url = url
        self._url_parse = urlparse(url, scheme='https')
        mongo_connect = MongoClient('mongodb://localhost:27017')
        self.mongo_db = mongo_connect['magnit_parse']

    def get_response_url(self, url):
        return requests.get(url, headers=self.__headers).text

    def get_soup(self, url):
        return BeautifulSoup(self.get_response_url(url), 'lxml')

    def load_product(self, products):
        for product in products:
            if len(product.attrs.get('class')) > 2 or product.attrs.get('href')[0] != '/':
                continue
            product_url = f'{self._url_parse.scheme}://{self._url_parse.hostname}{product.attrs.get("href")}'
            product_soup = self.get_soup(product_url)
            product_data = self.fill_in_dict(product_soup, product_url)
            self.save_product_to_db(product_data)

    def parse(self):
        soup = self.get_soup(self.url)
        catalog = soup.find('div', attrs={'class': "сatalogue__main"})
        products = catalog.findChildren('a', attrs={'class': 'card-sale'})
        self.load_product(products)

    def fill_in_dict(self, tmp_dict, url):
        _ = {'url': url}
        for param_product, val in self.product_template.items():
            try:
                if param_product == 'old_price' or param_product == 'new_price':
                    _[param_product] = int(tmp_dict.find(val[0], attrs={'class': val[1]}).find('span', attrs={
                        'class': 'label__price-integer'}).string) + float(
                        '0.' + tmp_dict.find(val[0], attrs={'class': val[1]}).find('span', attrs={
                            'class': 'label__price-decimal'}).string)
                    continue
                elif param_product == 'image_url':
                    _[param_product] = tmp_dict.find(val[0], attrs={'class': val[1]}).find('img')[val[2]]
                    continue

                elif param_product == 'date_from':
                    tmp_str = tmp_dict.find(val[0], attrs={'class': val[1]}).string.split('по')
                    _[param_product] = parse_date(self.replace_month_in_string(tmp_str[0].strip()))
                    _['date_to'] = parse_date(self.replace_month_in_string(tmp_str[1].strip()))
                    if _[param_product] >= _['date_to']:
                        _['date_to'] = _['date_to'] +  datetime.timedelta(year=1)
                    continue

                elif param_product == 'date_to':
                    continue

                else:
                    _[param_product] = getattr(tmp_dict.find(val[0], attrs={'class': val[1]}), val[2])
                    continue

            except Exception as e:
                _[param_product] = None
        return _

    def replace_month_in_string(self, text):
        args_dict = {'января': 'january',
                     'февраля': 'February',
                     'марта': 'March',
                     'апреля': 'April',
                     'мая': 'May',
                     'июня': 'June',
                     'июля': 'July',
                     'августа': 'August',
                     'сентября': 'September',
                     'октября': 'October',
                     'ноября': 'November',
                     'декабря': 'December', }
        t = text.lower()
        for key in args_dict.keys():
            if t.find(key) > 0:
                return t.replace(key, str(args_dict[key])).replace('с', '')

    def save_product_to_db(self, prod):

        collection = self.mongo_db['magnit' + self._date_point]
        collection.insert_one(prod)


if __name__ == '__main__':
    p = magnitDataMinePromo('https://magnit.ru/promo/')
    p.parse()
