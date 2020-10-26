# -*- coding: utf-8 -*-
import requests

import datetime as d
import database as db
import re
import json

from urllib.parse import urlparse
from bs4 import BeautifulSoup


class geekbrainsDataMinePosts():
    __headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
    }

    api_comments = 'https://geekbrains.ru/api/v2/comments'
    api_comments_params = {'commentable_type': 'Post',
                           'commentable_id': int(),
                           'order': 'desc',
                           }

    def __init__(self, url):
        self.url = url
        self._url_parse = urlparse(url, scheme='https')


    def get_html_txt(self, url, params):
        return requests.get(url, headers=self.__headers, params=params, ).text

    def get_soup(self, url, params):
        return BeautifulSoup(self.get_html_txt(url, params), 'lxml')

    def get_post(self):
        soup = self.get_soup(self.url, params={})
        # Идём по пагинации, для начала смотрим последнюю стр.
        last_one = int(soup.find('ul', attrs={'class': 'gb__pagination'}).find_all('li')[-2].find('a').text)

        while last_one:  # Шагаем страницами начиная с последней
            soup = self.get_soup(self.url, params={'page': last_one})
            posts_on_page = soup.find_all('div', attrs={'class': 'post-item event'})
            for post in posts_on_page:
                yield post

            last_one = last_one - 1

        return False

    def parce(self):
        for post in self.get_post():  # Запускаем генератор для каждого линка на пост
            post_link = post.find('a', attrs={'class': 'post-item__title'})
            post_url = f'{self._url_parse.scheme}://{self._url_parse.hostname}{post_link.attrs.get("href")}'

            print(post_url)
            self.push_to_db_post(self.get_soup(post_url, params={}), post_url)


    def get_dict_comments(self, post_id):

        def get_comment_children(children, comments):
            comment = children['comment']
            if comment['children'].__len__() > 0:
                get_comment_children(comment['children'][0], comments)
            comment_dict = {'writer': comment['user']['full_name'],
                            'date':  d.datetime.strptime(comment['created_at'] ,'%Y-%m-%dT%H:%M:%S.%f%z'),
                            'url': comment['user']['url'],
                            'text': comment['body']}
            comments[comment['id']] = comment_dict

        self.api_comments_params['commentable_id'] = post_id
        comments = {}
        json_response_comments = json.loads(self.get_html_txt(self.api_comments, self.api_comments_params))
        for comment in json_response_comments:
            get_comment_children(comment, comments)

        return comments



    def push_to_db_post(self, body_post, post_url):
        post_template = {
            'post_header': lambda body_post: body_post.find('h1', attrs={'class': 'blogpost-title'}).text,
            'img': lambda body_post: str(body_post.find('div', attrs={'class': 'blogpost-content content_text content js-mediator-article'}).find('img')['src']),
            'date': lambda body_post: d.datetime.strptime(body_post.find('div', attrs={'class': 'blogpost-date-views'}).find('time')['datetime'],'%Y-%m-%dT%H:%M:%S%z'),
            'autor': lambda body_post: body_post.find('div', attrs={'class': 'col-md-5 col-sm-12 col-lg-8 col-xs-12 padder-v'}).find('div', attrs={'itemprop': "author"}).text,
            'comments': [],
            # body > div.gb__main-wrapper > div.page-content > div.container > section > div > article > div.m-t-xl > comments > div > div.relative > section
            'list_of_tags': lambda body_post: body_post.find_all('a', href=re.compile('\/posts\?tag\=.*')),

        }

        post = {
            'url': post_url,
            'url_scheme_parse': self._url_parse,
        }
        for key, value in post_template.items():
            try:
                if key == 'comments':
                    post[key] = self.get_dict_comments(body_post.find('comments').attrs.get('commentable-id'))
                elif key == 'list_of_tags':
                    _ = []
                    for i, tag in enumerate(value(body_post)):
                        dict_tag = {}
                        dict_tag['name'] = tag.text
                        dict_tag['url'] = f'{self._url_parse.scheme}://{self._url_parse.hostname}{tag.get("href")}'
                        _.append(dict_tag)
                    post[key] = _
                else:
                    post[key] = value(body_post)
            except Exception as e:
                print(e)
                post[key] = None

        self.db_session = db.dbConnector()
        self.db_session.load_to_db(post)



if __name__ == '__main__':
    data_main = geekbrainsDataMinePosts('https://geekbrains.ru/posts')
    data_main.parce()
