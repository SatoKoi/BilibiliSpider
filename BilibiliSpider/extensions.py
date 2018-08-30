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
        try:
            res = cursor.execute("select user, passwd from myaccount where md5_passwd='{}' and id={}"
                                 .format(crawler.settings['SECRET_KEY'], crawler.settings['ID']))

            if res == 1:
                crawler.remote_account = {}
                crawler.remote_account['REMOTE_MYSQL_USER'], crawler.remote_account['REMOTE_MYSQL_PASSWD'] = cursor.fetchone()
        except:
            crawler.remote_account = {}
        return cls(crawler)


class ParseOnlineExtension(object):
    """获取在线人数扩展"""
    def __init__(self, interval, conn):
        from numbers import Integral
        assert isinstance(interval, Integral) and interval > 0, """
        ONLINE_INTERVAL must be a positive integer
        """
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
        o = cls(interval, conn)
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


class BQuickReplyOnBangumi(object):
    def __init__(self, conn, user_id, flush_frequency):
        self.conn = conn
        self.user_id = user_id
        self.flush_frequency = flush_frequency

    @classmethod
    def from_crawler(cls, crawler):
        conn = StrictRedis(
            host=crawler.settings.get('REDIS_HOST', '127.0.0.1'),
            port=crawler.settings.get('REDIS_PORT', 6379),
            db=0,
            password=crawler.settings.get('REDIS_PARAMS', {}).get('password', None)
        )
        user_id = crawler.settings.get("DEDE_USER_ID", 1)
        flush_frequency = crawler.settings.get("FLUSH_FREQUENCY", 30)
        o = cls(conn, user_id, flush_frequency)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_opened(self, spider):
        self.task = task.LoopingCall(self.next_request, spider)
        self.task.start(self.flush_frequency)

    def next_request(self, spider):
        self.conn.lpush("bilibili:urls", spider.api_urls.get('bangumi').format(id=self.user_id))

    def spider_closed(self, spider, reason):
        if self.task and self.task.running:
            self.task.stop()