# -*- coding: utf-8 -*-

from mygrades.models import ScrapyItem
import json

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class ScrapegradesPipeline(object):
    def __init__(self, unique_id, *args, **kwargs):
        self.unique_id = unique_id
        self.items = []

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            unique_id=crawler.settings.get(
                "unique_id"
            )  # this will be passed from django view
        )

    def close_spider(self, spider):
        # And here we are saving our crawled data with django models.
        print(self.items)
        item = ScrapyItem()
        item.unique_id = self.unique_id
        item.data = json.dumps(self.items)
        item.save()

    def process_item(self, item, spider):
        self.items.append(item)
        return item
