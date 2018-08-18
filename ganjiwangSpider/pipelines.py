# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class GanjiwangspiderPipeline(object):
    def __init__(self):
        self.file = open('./gzershoufang.txt', 'w', encoding='utf-8', errors='ignore')

    def process_item(self, item, spider):
        line = str(item) + '\r\n'
        self.file.write(line)
        self.file.flush()
        return item

    def __del__(self):
        self.file.close()
