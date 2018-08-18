# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import re
import time
from io import BytesIO
from PIL import Image
from scrapy import Request
from scrapy import signals
import random
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from ganjiwangSpider.settings import USER_AGENTS, PROXIES
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as Ec
from selenium.webdriver.support.wait import WebDriverWait
from scrapy.http import HtmlResponse
from ganjiwangSpider.utils.chaojiyingVirifyCode import Chaojiying_Client


class RandomUAMiddleware(object):
    """随机UA代理中间件"""

    def process_request(self, request, spider):

        user_agent = random.choice(USER_AGENTS)
        request.headers.setdefault('User-Agent', user_agent)


class RandomIPMiddleware(HttpProxyMiddleware):
    """随机IP代理"""

    def process_request(self, request, spider):
        proxy = random.choice(PROXIES)
        # IP = 'http://' + proxy['ip_port']
        IP = 'http://'+proxy
        request.meta['proxy'] = IP


class VerifyCodeMiddleware(object):
    """识别验证码"""
    def __init__(self):
        self.CHAOJIYING_USERNAME = 'getcode'
        self.CHAOJIYING_PASSWORD = 'getcode'
        self.CHAOJIYING_SOFT_ID = 897078
        self.CHAOJIYING_KIND = 9104

    def open_selenium(self, timeout=None):
        """打开selenium调用无头浏览器"""
        self.timeout = timeout
        # 无头浏览器模式
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        self.wait = WebDriverWait(self.browser, timeout)
        # self.browser.set_page_load_timeout(self.timeout)

    def close_selenium(self):
        """关闭浏览器"""
        self.browser.close()

    def process_request(self, request, spider):

        url = request.url
        pat = 'callback.ganji.com/firewall/'
        is_firewall = re.search(pat, url)
        if is_firewall:

            self.chaojiying = Chaojiying_Client(
                self.CHAOJIYING_USERNAME, self.CHAOJIYING_PASSWORD, self.CHAOJIYING_SOFT_ID)
            self.open_selenium(timeout=5)
            loop = 0
            while is_firewall:
                url, im_id = self.handle_code(url)
                if re.search(pat, url):
                    self.chaojiying.ReportError(im_id)
                else:
                    is_firewall = False
                    self.close_selenium()
                loop += 1
                if loop > 5:
                    self.close_selenium()
                    return Request(url)
            return None
        else:
            return None

    def handle_code(self, url):
        """处理验证码"""

        self.browser.get(url)
        self.first_click()
        # time.sleep(0.5)
        image = self.get_image()
        bytes_array = BytesIO()
        image.save(bytes_array, format='PNG')
        result = self.chaojiying.PostPic(bytes_array.getvalue(), self.CHAOJIYING_KIND)
        # print(result)
        locations = self.get_point(result)
        im_id = self.get_im_id(result)
        self.touch_click_words(locations)
        # print(self.browser.page_source)
        # self.close_selenium()
        self.browser.find_element_by_xpath('//*[@id="ISDCaptcha"]/div/div[3]/span').click()
        # self.wait.until(Ec.presence_of_all_elements_located())
        self.browser.implicitly_wait(10)
        time.sleep(0.1)

        print(self.browser.current_url)
        return self.browser.current_url, im_id

    def first_click(self):
        """进入验证码前的点击"""
        botton = self.wait.until(Ec.element_to_be_clickable((By.ID, 'btnSubmit')))
        botton.click()
        # self.browser.find_element_by_id(id_='btnSubmit').click()

    def get_picture(self):
        """
        获取图片对象
        :return: 图片对象
        """
        picture = self.wait.until(Ec.presence_of_element_located((By.XPATH, '//*[@id="ISDCaptcha"]/div/div[2]/img')))
        # picture = self.browser.find_element_by_xpath('//*[@id="ISDCaptcha"]/div/div[2]/img')
        return picture

    def get_position(self):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        picture = self.get_picture()
        location = picture.location
        size = picture.size
        top, bottom = location['y'], location['y'] + size['height']
        left, right = location['x'], location['x'] + size['width']
        return (top, bottom, left, right)

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_image(self):
        """
        从网页截图中截取对应的验证码图片
        :return: 图片Image对象
        """
        top, bottom, left, right = self.get_position()
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        return captcha

    def get_point(self, captcha_result):
        """
        解析识别的结果
        :param captcha_result: 识别结果
        :return: 转化后的结果
        """
        groups = captcha_result.get('pic_str').split('|')
        locations = [[int(number) for number in group.split(',')] for group in groups]
        return locations

    def get_im_id(self, captcha_result):
        return captcha_result.get('pic_id')

    def touch_click_words(self, locations):
        """
        点击图片验证码
        :param locations: 点击位置
        :return: None
        """
        for location in locations:
            # print(location)
            ActionChains(self.browser).move_to_element_with_offset(self.get_picture(),
                        location[0], location[1]).click().perform()
            time.sleep(0.3)


class GanjiwangspiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class GanjiwangspiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
