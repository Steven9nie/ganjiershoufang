# -*- coding: utf-8 -*-
# @File : start.py
import scrapy.cmdline


def main():
    scrapy.cmdline.execute(['scrapy', 'crawl', 'ershoufang'])


if __name__ == '__main__':
    main()

