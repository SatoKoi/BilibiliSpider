# -*- coding:utf-8 -*-
import pymysql

from twisted.internet import task
from scrapy import signals
from redis import StrictRedis, ConnectionPool


class GetRemotePasswordExtension(object):
    """获取远程连接参数的扩展"""
    def __init__(self, crawler):
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        """获取远程连接参数"""
        connection = pymysql.connect(
            user=crawler.settings['MYSQL_USER'],
            host=crawler.settings['MYSQL_HOST'],
            port=crawler.settings['MYSQL_PORT'],
            passwd=crawler.settings['MYSQL_PASSWORD'],
            database=crawler.settings['MYSQL_ACDB'],
            charset=crawler.settings['MYSQL_CHARSET']
        )
        cursor = connection.cursor()
        res = cursor.execute("select user, passwd from myaccount where md5_passwd='{}' and id={}"
                             .format(crawler.settings['SECRET_KEY'], crawler.settings['ID']))

        if res == 1:
            crawler.remote_account = {}
            crawler.remote_account['REMOTE_MYSQL_USER'], crawler.remote_account['REMOTE_MYSQL_PASSWD'] = cursor.fetchone()
        return cls(crawler)


class ParseOnlineExtension(object):
    """获取在线人数扩展"""
    def __init__(self, stats, interval, conn):
        from numbers import Integral
        assert isinstance(interval, Integral) and interval > 0, """
        ONLINE_INTERVAL must be a positive integer
        """
        self.stats = stats
        self.interval = interval
        self.task = None
        self.conn = conn

    @classmethod
    def from_crawler(cls, crawler):
        interval = crawler.settings.get('ONLINE_INTERVAL', 1800)
        pool = ConnectionPool(
            host=crawler.settings.get('REDIS_HOST', '127.0.0.1'),
            port=crawler.settings.get('REDIS_PORT', 6379),
            db=0,
            password=crawler.settings.get('REDIS_PARAMS', {}).get('password', None)
        )
        conn = StrictRedis(connection_pool=pool)
        o = cls(crawler.stats, interval, conn)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_opened(self, spider):
        self.task = task.LoopingCall(self.next_request, spider)
        self.task.start(self.interval)

    def next_request(self, spider):
        self.conn.lpush("bilibili:urls", spider.api_urls.get('online'))

    def spider_closed(self, spider, reason):
        if self.task and self.task.running:
            self.task.stop()
