# -*- coding: utf-8 -*-
import os
import pymysql
import hashlib
import functools
import json

from scrapy import Request
from scrapy.utils.misc import load_object
from scrapy.xlib.pydispatch import dispatcher
from scrapy.signals import *
from scrapy.utils.python import to_bytes
from twisted.enterprise import adbapi
from twisted.internet.threads import deferToThread
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from scrapy_redis.pipelines import RedisPipeline
from scrapy_redis import connection, defaults
from scrapy.utils.serialize import ScrapyJSONEncoder
from threading import Lock
from .settings import JSON_EXPORT_LOCATION, IMAGES_DIRECTORY_NAME, SQL_DATETIME_FORMAT
from .items import *

default_serialize = ScrapyJSONEncoder().encode


class JsonExporterPipeline(object):
    """调用scrapy提供的json export 导出json文件"""
    # TODO: export无法写入json数据, 求解
    def __init__(self, name, location, items=None):
        try:
            # self.file = open(os.path.join(location, name), 'a+', encoding='utf8')
            self.file = open(os.path.join(location, name), 'wb')
        except:
            dispatcher.connect(self.handle_exception, signal=spider_error)
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()  # 开始导出
        self.items = items

    @classmethod
    def from_settings(cls, settings):
        params = {}
        params['name'] = settings.get("JSON_FILE_NAME", "export.json")
        params['location'] = settings.get("JSON_EXPORT_LOCATION",
                                          os.path.dirname(os.path.abspath(__file__)))
        params['items'] = settings.get("JSON_ITEMS", [])
        return cls(**params)

    def close_spider(self, spider):
        """spider退出时调用"""
        self.file.close()  # 关闭文件

    def export_item(self, item):
        """自定义的export方法"""
        try:
            json.dump(item, self.file, ensure_ascii=False, indent=4, separators=(',', ':'))
        except Exception as e:
            dispatcher.connect(self.handle_exception, signal=spider_error)

    def finish(self, spider):
        """结束导出"""
        self.exporter.finish_exporting()

    def process_item(self, item, spider):
        """处理项目"""
        for i in self.items:
            if isinstance(item, eval(i)):
                # self.export_item(self.translate_datetime(item))  # 导出item数据
                self.exporter.export_item(self.translate_datetime(item))
                dispatcher.connect(self.finish, signal=item_scraped)
        return item

    def handle_exception(self, spider, reason):
        spider.logger.error(reason)

    def translate_datetime(self, item):
        """将不可序列化的datetime对象转换为str对象"""
        for k, v in item.items():
            if isinstance(v, datetime):
                item[k] = datetime.strftime(v, SQL_DATETIME_FORMAT)
        return item


class MysqlTwistPipeline(object):
    """异步化的Mysql处理数据管道"""

    def __init__(self, dbpool, items=None):
        self.dbpool = dbpool
        self.items = items

    @classmethod
    def from_crawler(cls, crawler):
        """每次初始化加载, 都会将settings.py中的设置传入到:param settings中"""
        api_params = dict(host=crawler.settings['REMOTE_MYSQL_HOST'],
                          user=crawler.remote_account.get('REMOTE_MYSQL_USER', 'root'),
                          passwd=crawler.remote_account.get('REMOTE_MYSQL_PASSWD', '123456'),
                          port=crawler.settings['REMOTE_MYSQL_PORT'],
                          db=crawler.settings['REMOTE_MYSQL_DATABASE'],
                          charset=crawler.settings['REMOTE_MYSQL_CHARSET'],
                          cursorclass=pymysql.cursors.DictCursor,  # 必须值
                          use_unicode=True,
                          )
        # 调用twist异步模块的连接池, arg1: 需要调用的Mysql操作库名称, arg2: 连接参数
        conn = pymysql.connect(**api_params)
        dbpool = adbapi.ConnectionPool('pymysql', **api_params)
        items = crawler.settings.get("MYSQL_ITEMS", [])
        return cls(dbpool, items)  # 对自身进行实例化

    def process_item(self, item, spider):
        """使用twisted模块将mysql操作变成异步执行
        :function runInteraction: arg1: sql插入逻辑函数 arg2: 传入参数
        :function addErrorback: arg1: 处理异常逻辑函数, arg*: 传入参数
        """
        # 异步执行完成后, 返回一个Deferred对象
        for i in self.items:
            if isinstance(item, eval(i)):
                query = self.dbpool.runInteraction(self.do_insert, item)
                query.addErrback(self.handle_error, item, spider)
        return item

    def handle_error(self, failure, item, spider):
        """异步处理插入操作的异常"""
        spider.logger.warn(failure)

    def do_insert(self, cursor, item):
        """:param cursor: 接受cursorclass中的cursor
        异步化操作后, runInteraction将自动commit, 不需要手动
        """
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)


class MysqlPipeline(object):
    def __init__(self, conn, items):
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.items = items

    @classmethod
    def from_crawler(cls, crawler):
        """每次初始化加载, 都会将settings.py中的设置传入到:param settings中"""
        api_params = dict(host=crawler.settings['REMOTE_MYSQL_HOST'],
                          user=crawler.remote_account.get('REMOTE_MYSQL_USER', 'root'),
                          password=crawler.remote_account.get('REMOTE_MYSQL_PASSWD', '123456'),
                          port=crawler.settings['REMOTE_MYSQL_PORT'],
                          db=crawler.settings['REMOTE_MYSQL_DATABASE'],
                          charset=crawler.settings['REMOTE_MYSQL_CHARSET'],
                          autocommit=True
                          )
        # 调用twist异步模块的连接池, arg1: 需要调用的Mysql操作库名称, arg2: 连接参数
        conn = pymysql.connect(**api_params)
        items = crawler.settings.get("MYSQL_ITEMS", [])
        return cls(conn, items)  # 对自身进行实例化

    def process_item(self, item, spider):
        for i in self.items:
            if isinstance(item, eval(i)):
                self.do_insert(self.cursor, item)
        return item

    def do_insert(self, cursor, item):
        """:param cursor: 接受cursorclass中的cursor
        异步化操作后, runInteraction将自动commit, 不需要手动
        """
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)


class RedisPipeline(RedisPipeline):
    """可控行为的redis 管道"""
    def __init__(self, server,
                 key=defaults.PIPELINE_KEY,
                 serialize_func=default_serialize,
                 items=None):
        super(RedisPipeline, self).__init__(server,
                                            key=key,
                                            serialize_func=serialize_func
                                            )
        self.lock = Lock()
        self.items = items

    @classmethod
    def from_settings(cls, settings):
        params = {
            'server': connection.from_settings(settings),
        }
        if settings.get('REDIS_ITEMS_KEY'):
            params['key'] = settings['REDIS_ITEMS_KEY']
        if settings.get('REDIS_ITEMS_SERIALIZER'):
            params['serialize_func'] = load_object(
                settings['REDIS_ITEMS_SERIALIZER']
            )
        params['items'] = settings.get('REDIS_ITEMS', [])
        return cls(**params)

    def process_item(self, item, spider):
        for i in self.items:
            with self.lock:
                if isinstance(item, eval(i)):
                    spider.key = i
                    return deferToThread(self._process_item, item, spider)
        return item

    def item_key(self, item, spider):
        return self.key % {'spider': spider.name, 'item': spider.key}


class ExcelExporterPipeline(object):
    """Excel表导出管道"""

    def process_item(self, item, spider):
        # TODO: 实现item下的save_to_excel方法
        if hasattr(item, "save_to_excel"):
            item.save_to_excel()
        return item


class GeneralImagePipeline(ImagesPipeline):
    """通用图片下载管道"""
    IMAGES_DIRECTORY_NAME = 'default'

    def __init__(self, store_uri, download_func=None, settings=None):
        super(GeneralImagePipeline, self).__init__(store_uri, settings=settings,
                                                   download_func=download_func)

        resolve = functools.partial(self._key_for_pipe,
                                    base_class_name="ImagesPipeline",
                                    settings=settings)
        self.image_directory_name = settings.get(
            resolve("IMAGES_DIRECTORY_NAME"),
            self.IMAGES_DIRECTORY_NAME
        )

    def item_completed(self, results, item, info):
        """:param results: 二元组, 包含一个访问成功与否的信息, 与一个访问成功后返回的信息(字典)"""
        if 'img_url' in item:
            for ok, value in results:
                image_file_path = value['path']
                item['img_path'] = image_file_path
            return item

    def file_path(self, request, response=None, info=None):
        """copy from super class, only changed the store location of file path"""
        def _warn():
            from scrapy.exceptions import ScrapyDeprecationWarning
            import warnings
            warnings.warn('ImagesPipeline.image_key(url) and file_key(url) methods are deprecated, '
                          'please use file_path(request, response=None, info=None) instead',
                          category=ScrapyDeprecationWarning, stacklevel=1)

        if not isinstance(request, Request):
            _warn()
            url = request
        else:
            url = request.url

        if not hasattr(self.file_key, '_base'):
            _warn()
            return self.file_key(url)
        elif not hasattr(self.image_key, '_base'):
            _warn()
            return self.image_key(url)

        image_guid = hashlib.sha1(to_bytes(url)).hexdigest()
        return '{}/{}'.format(self.image_directory_name, image_guid)