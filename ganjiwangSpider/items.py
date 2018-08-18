# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GanjiwangspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    # 要爬取的字段
    # title, href, size, address, feature, info, tel
    title = scrapy.Field()
    href = scrapy.Field()
    size = scrapy.Field()
    address = scrapy.Field()
    feature = scrapy.Field()
    info = scrapy.Field()
    contact = scrapy.Field()
    tel = scrapy.Field()
