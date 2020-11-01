# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class HhparsPipeline:

    def __init__(self):
        mongo_connect = MongoClient('mongodb://localhost:27017')
        self.mongodb = mongo_connect['hh']

    def process_item(self, item, spider):
        collection = self.mongodb[type(item).__name__]
        collection.insert_one(item)
        return item
