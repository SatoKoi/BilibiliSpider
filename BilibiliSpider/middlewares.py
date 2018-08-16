# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import re
import json
import time
import pymysql
import random
import urllib

from urllib.parse import urlparse
from selenium.webdriver import PhantomJS, Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from scrapy import signals
from scrapy.http import HtmlResponse
from fake_useragent import UserAgent

from tools.getIp import GetIp
from .utils.metrics import GetNumber
from .scripts import Script
from .settings import REMOTE_MYSQL_CHARSET, REMOTE_MYSQL_HOST, REMOTE_MYSQL_PORT, \
    REMOTE_MYSQL_DATABASE, REMOTE_MYSQL_TOOLDB
from .map.defaults import REG_PATTERN




class BilibilispiderSpiderMiddleware(object):
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


class SeleniumDownloadMiddleware(object):
    """
    Spider下载器中间件
    将使用selenium处理需要的request
    """

    def __init__(self, script, get):
        self.script = script
        self.get = get

    @classmethod
    def from_crawler(cls, crawler):
        s = cls(Script(), GetNumber())
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        """根据url判断是否进行处理"""
        parse_res = urlparse(request.url)
        if parse_res.netloc in spider.allowed_domains:
            browser = request.meta.get("browser")
            if not browser:
                while True:
                    browser = spider.queue.get(timeout=5)
                    if browser:
                        break
            # browser.implicitly_wait(6)
            # browser.get(request.url)
            spider.browser.implicitly_wait(6)
            spider.browser.get(request.url)
            try:
                # browser.implicitly_wait(2)
                # browser.execute_script(self.script.scrollToBottom)
                spider.browser.implicitly_wait(2)
                spider.browser.execute_script(self.script.scrollToBottom)
                time.sleep(2)
            except Exception as e:
                spider.logger.error(e)
            # response = HtmlResponse(request.url, body=browser.page_source, request=request, encoding='utf-8')
            response = HtmlResponse(request.url, body=spider.browser.page_source, request=request, encoding='utf-8')
            response.meta['parse_res'] = parse_res
            response.meta['browser'] = browser
            return response
        return None

    def process_response(self, request, response, spider):
        """使用selenium获取得到的页面source替换response, 并执行相应脚本"""
        # response = response.replace(body=spider.browser.page_source)
        browser = response.meta.get('browser')
        parse_res = response.meta['parse_res']
        # 如果是视频详情页
        if re.match(REG_PATTERN['video'], parse_res.path, re.I):
            cookie = spider.browser.get_cookie(name='stardustvideo')
            # cookie = browser.get_cookie(name='stardustvideo')
            # 尝试使用新版功能
            try:
                spider.browser.execute_script(self.script.tryNewPage)
                # browser.execute_script(self.script.tryNewPage)
                time.sleep(5)
            except Exception as e:
                spider.logger.error(e)
            try:
                likes = spider.browser.find_element_by_xpath("//span[@class='like']")
                page = spider.browser.find_element_by_xpath("//div[@class='page-jump']/span")
                comments = spider.browser.find_element_by_xpath("//span[contains(@class, 'results')]")
                # likes = browser.find_element_by_xpath("//span[@class='like']")
                # page = browser.find_element_by_xpath("//div[@class='page-jump']/span")
                # comments = browser.find_element_by_xpath("//span[contains(@class, 'results')]")
                response.meta['likes'] = likes.text  # 视频点赞数
                response.meta['page_nums'] = self.get(page.text)[0]  # 视频评论页数
                response.meta['comments'] = self.get(comments.text)[0]   # 视频评论数
            except Exception as e:
                spider.logger.error(e)
            finally:
                # 更改cookie, 每次访问新的video页面指向旧版
                cookie = spider.browser.get_cookie(name='stardustvideo')
                # cookie = browser.get_cookie(name='stardustvideo')
                if cookie and int(cookie.get('value')) == 1:
                    spider.browser.delete_cookie(name='stardustvideo')
                    # browser.delete_cookie(name='stardustvideo')
                    cookie['value'] = '0'
                    spider.browser.add_cookie(cookie)
                    # browser.add_cookie(cookie)
        if re.match(REG_PATTERN['article'], parse_res.path, re.I):
            try:
                spider.browser.execute_script(self.script.articleSTB)
                # browser.execute_script(self.script.articleSTB)
                time.sleep(5)
                e = spider.browser.find_element_by_xpath("//div[contains(@class, 'paging-box')]/span[@class='result']")
                # e = browser.find_element_by_xpath("//div[contains(@class, 'paging-box')]/span[@class='result']")
                response.meta['page_nums'] = self.get(e.text)[0]
            except Exception as e:
                spider.logger.error(e)
        return response

    def process_exception(self, request, exception, spider):
        spider.logger.warn(exception)

    def spider_opened(self, spider):
        spider.logger.info('Spider %s start SeleniumDownloadMiddleware' % spider.name)


class RandomUserAgentMiddleware(object):
    """随机User-Agent代理中间件"""

    def __init__(self, crawler):
        super(RandomUserAgentMiddleware, self).__init__()
        self.ua = UserAgent()
        self.ua_type = crawler.settings.get("RANDOM_UA_TYPE", "random")
        # self.user_agent_list = crawler.settings.get("USER_AGENT_LIST", [])    # 从设置中获取USER_AGENT_LIST

    @classmethod
    def from_crawler(cls, crawler):
        s = cls(crawler)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):
        spider.logger.info('Spider %s start RandomUserAgentMiddleware' % spider.name)

    def process_request(self, request, spider):
        # 给请求头设置初始User-Agent, 从USER_AGENT_LIST随机选择
        # request.headers.setdefault("User-Agent", random.choice(self.user_agent_list))
        def get_ua(self):  # 闭包特性: 要将self传入, 否则会报错
            """动态获取self.ua的type值"""
            return getattr(self.ua, self.ua_type)

        request.headers.setdefault("User-Agent", get_ua(self))


class RandomProxyMiddleware(object):
    """随机IP代理中间件"""
    def __init__(self, conn):
        self.conn = conn
        self.ip_manager = GetIp(self.conn.cursor())

    @classmethod
    def from_crawler(cls, crawler):
        user, password = crawler.remote_account['REMOTE_MYSQL_USER'], crawler.remote_account['REMOTE_MYSQL_PASSWD']
        connection = pymysql.connect(
            user=user,
            host=REMOTE_MYSQL_HOST,
            password=password,
            database=REMOTE_MYSQL_TOOLDB,
            port=REMOTE_MYSQL_PORT,
            charset=REMOTE_MYSQL_CHARSET,
            autocommit=True
        )
        s = cls(connection)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        """设置动态ip代理, request将继续被处理"""
        # request.meta['proxy'] = self.ip_manager.get_random_ip()
        ip_list = ['http://47.106.72.198:8000', None]
        ip = random.choice(ip_list)
        if ip:
            request.meta['proxy'] = ip

    def spider_opened(self, spider):
        spider.logger.info('Spider %s start RandomProxyMiddle' % spider.name)


class DynamicRefererMiddleware(object):
    """动态更改Referer等参数"""
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        parse_res = urlparse(request.url)
        request.headers['Host'] = parse_res.netloc
        request.headers['Referer'] = request.url

    def spider_opened(self, spider):
        spider.logger.info('Spider %s start DynamicRefererMiddleware' % spider.name)


class PosturlParseMiddleware(object):
    """解析get方式的url参数并发送post方法至相对应的url中"""
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):
        spider.logger.info('Spider %s start PosturlParseMiddleware' % spider.name)

    def process_request(self, request, spider):
        parse_res = urlparse(request.url)
        if re.match(REG_PATTERN['reply'], parse_res.path):
            data = {}
            for query in parse_res.query.split('&'):
                s = query.split('=')
                if s[0] == "message":
                    # 对message进行urldecode
                    s[1] = urllib.parse.unquote(s[1])
                data.update({s[0]: s[1]})
            return HtmlResponse(request.url, body=json.dumps(data), request=request, encoding='utf8')