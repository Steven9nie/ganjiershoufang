# -*- coding: utf-8 -*-

import json
import re
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ganjiwangSpider.items import GanjiwangspiderItem


class ErshoufangSpider(CrawlSpider):

    name = 'ershoufang'
    allowed_domains = ['gz.ganji.com']
    start_urls = ['http://gz.ganji.com/fang5/o1/']

    rules = [Rule(LinkExtractor(allow=("fang5/o(\d+)/")),
                  callback='get_parse', follow=True)]

    def get_parse(self, response):

        dataList = response.xpath('//dl[@class="f-list-item-wrap f-clear"]')
        pat = '(\S+)'
        for d in dataList:
            title = d.xpath('.//a[@class="js-title value title-font"]/text()').extract()[0]
            href = 'http://gz.ganji.com' + d.xpath('.//a[@class="js-title value title-font"]/@href').extract()[0]
            sizeList = d.xpath('.//dd[@class="dd-item size"]//text()').extract()
            size = ''.join(re.findall(pat, ''.join(sizeList)))
            addressList = d.xpath('.//dd[@class="dd-item address"]/span//text()').extract()
            address = ''.join(re.findall(pat, ''.join(addressList)))
            featureList = d.xpath('.//dd[@class="dd-item feature"]//text()').extract()
            feature = ''.join(re.findall(pat, ''.join(featureList)))
            infoList = d.xpath('.//dd[@class="dd-item info"]//text()').extract()
            info = ''.join(re.findall(pat, ''.join(infoList)))

            request = scrapy.Request(url=href, callback=self.get_detail)
            request.meta['title'] = title
            request.meta['href'] = href
            request.meta['size'] = size
            request.meta['address'] = address
            request.meta['feature'] = feature
            request.meta['info'] = info
            yield request

    def get_detail(self, response):

        contact = response.xpath('//p[@class="name"]/text()').extract()[0].strip()

        phoneUrl = response.xpath('//div[@id="full_phone_show"]/@data-phone').extract()[0]
        purl = phoneUrl.replace('+', '%2B').replace('/', '%2F').replace('=', '%3D')
        Url = f'http://gz.ganji.com/ajax.php?dir=house&module=secret_phone&user_id=780848049&puid=3493460477&major_index=5&phone={purl}&isPrivate=1'
        request = scrapy.Request(url=Url, callback=self.get_tel)
        request.meta['title'] = response.meta['title']
        request.meta['href'] = response.meta['href']
        request.meta['size'] = response.meta['size']
        request.meta['address'] = response.meta['address']
        request.meta['feature'] = response.meta['feature']
        request.meta['info'] = response.meta['info']
        request.meta['contact'] = contact
        yield request

    def get_tel(self, response):
        res = json.loads(response.body)
        tel = res['secret_phone']
        item = GanjiwangspiderItem()
        item['title'] = response.meta['title']
        item['href'] = response.meta['href']
        item['size'] = response.meta['size']
        item['address'] = response.meta['address']
        item['feature'] = response.meta['feature']
        item['info'] = response.meta['info']
        item['tel'] = tel
        item['contact'] = response.meta['contact']
        yield item
