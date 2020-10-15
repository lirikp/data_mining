import json
import requests
import pandas as pd
import time
import os

from pathlib import Path

PATH_LOAD = 'products'
FILE_LOAD_IDS = 'table_product.csv'
TIMER = 0.1  # секунды


class Parser5ka:
    __params = {
        'records_per_page': 20,
    }

    db_id_product: pd

    __headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0',
    }

    append_product = {
        "name": "",
        "code": "",
        "products": [],  # список словарей товаров соответсвующих данной категории
    }

    def __init__(self, start_url):
        self.start_url = start_url
        self.init_last_load_id()  # Грузим если существует файл с идами уже отгруженных продуктов если нет, то создаём таблицу
        self.check_path_files()  # Проверяем наличие папки для загрузки данных, если нет создаём

    def check_path_files(self):
        if not os.path.exists(Path.cwd() / PATH_LOAD):
            os.makedirs(Path.cwd() / PATH_LOAD)

    def init_last_load_id(self):
        if os.path.exists(FILE_LOAD_IDS):
            self.db_id_product = pd.read_csv(FILE_LOAD_IDS)
        else:
            self.db_id_product = pd.DataFrame(columns=('id', 'group_name', 'group_code', 'date_in', 'name'))

    def to_table(self, *args, **kwargs):  # Строчка в таблицу айдишников, отгружено!
        self.db_id_product = self.db_id_product.append(kwargs, ignore_index=True)

    def parse(self, url=None):
        params = self.__params

        # Берём категории https://5ka.ru/api/v2/categories/
        parent_group_code = requests.get('https://5ka.ru/api/v2/categories/', params=params, headers=self.__headers)
        group_code = parent_group_code.json()
        for code in group_code:  # ПРоходим по всем категориям
            if not url:
                url = self.start_url

            self.append_product['name'] = code["parent_group_name"]
            self.append_product['code'] = code["parent_group_code"]
            params['categories'] = code[
                "parent_group_code"]  # Добавляем параметры чтобы можно было залезть сразу на склад
            params['store'] = ''

            print(f'Категория: {code["parent_group_name"]}')
            while url:

                response = requests.get(url, params=params, headers=self.__headers)
                print(f'Load page: {response.request.url} RESPONSE_CODE: {response.status_code}')

                data: dict = response.json()
                url = data['next']

                for product in data['results']:  # По странично заливаем в массив из категории продукты
                    if not self.check_load(id=product[
                        "id"]):  # !!! ПРоверяем не случилась какая нибудь новая акция на товар в данной категории сверяем со списком общих идов товара из таблицы.
                        self.append_product['products'].append(product)
                        self.to_table(id=product['id'],
                                      group_name=code["parent_group_name"],
                                      group_code=code["parent_group_code"],
                                      name=product['name'],
                                      date_in=time.strftime("%m/%d/%Y, %H:%M:%S"))

                        print(f'    load id: {product["id"]}')
                    else:
                        print(f'NOT load id: {product["id"]}')

                time.sleep(TIMER)

            if self.append_product['products'].__len__():
                self.save_to_json_file(category=code["parent_group_code"], category_name=code["parent_group_name"])
                self.page_load()  # отбивка удачно подгруженой категории

    def check_load(self, **kwargs):
        filter = self.db_id_product['id'].isin([kwargs['id']])
        if self.db_id_product[filter].count().id:
            return True
        else:
            return False

    def save_to_json_file(self, **kwargs):
        file_name = f'products/{kwargs["category"]}_{kwargs["category_name"]}.json'

        with open(file_name, 'w', encoding='UTF-8') as file:
            json.dump(self.append_product, file, ensure_ascii=False)

    def page_load(self):
        # Дропаем старый файл с айдишниками отгруженных
        if os.path.exists(FILE_LOAD_IDS):
            os.remove(FILE_LOAD_IDS)
        # Создаём новый с отгруженными
        self.db_id_product.to_csv(FILE_LOAD_IDS, index=False, encoding='utf-8', sep=',')


if __name__ == '__main__':
    parser = Parser5ka('https://5ka.ru/api/v2/special_offers/')
    parser.parse()
