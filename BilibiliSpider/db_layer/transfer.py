# -*- coding:utf-8 -*-
import sys, os
from redis import StrictRedis, ConnectionPool

base_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, base_dir)

from db_layer.item_map import *
from db_layer.logs import Logger
from concurrent.futures import ThreadPoolExecutor

import time
import logging
import json
import pymysql
from threading import Lock


class Transfer(object):
    def __init__(self, mysql, redis, loggers, items, chunk_size=10):
        self.mysql = mysql
        self.redis = redis
        self.items = items
        self.loggers = loggers
        self.chunk_size = chunk_size
        self.base_key = "bilibili:%(item)s"

    def transfer(self, item):
        with self.mysql.cursor() as cursor:
            while True:
                key = self.base_key % {'item': item}
                key_len = self.redis.llen(key)
                if key_len:
                    chunk_size = key_len if self.chunk_size > key_len else self.chunk_size
                    item_cls = eval(item)
                    with self.redis.pipeline() as pipe:
                        for _ in range(chunk_size):
                            pipe.lpop(key)
                        res_queue = pipe.execute()
                        for row_data in res_queue:
                            try:
                                data = item_cls(json.loads(row_data, encoding='utf8'))
                                self._transfer(cursor, item, data)
                            except Exception as e:
                                self.handle_exception(item, {}, e)
                else:
                    break

    def _transfer(self, cursor, item, data):
        insert_sql, params = data.get_insert_sql()
        try:
            with lock:
                cursor.execute(insert_sql, params)
        except Exception as e:
            self.handle_exception(item, data, e)
        else:
            self.handle_info(item, data)

    def handle_exception(self, item, data, exception):
        if data.get("sid"):
            data = CommentItem(data.d)
            insert_sql, params = data.get_insert_sql()
            try:
                with lock:
                    with self.mysql.cursor() as cursor:
                        cursor.execute(insert_sql, params)
            except Exception as e:
                self.loggers[1].error(item + ": " + str(data) + str(exception))
        else:
            self.loggers[1].error(str(exception))

    def handle_info(self, item, data):
        self.loggers[0].info(item + ": " + str(data))


if __name__ == '__main__':
    logger_one = Logger(__name__)
    logger_two = Logger(__name__)
    logger_one.add_file_handler("transfer_failure.log", level=logging.ERROR)
    logger_two.add_stream_handler()
    logger_two.add_file_handler("transfer_success.log", level=logging.INFO)
    pool = ConnectionPool(host='',
                          password='',
                          db=0,
                          port=6379
                          )
    conn = StrictRedis(connection_pool=pool)
    mysql = pymysql.connect(host='',
                            password='',
                            port=3306,
                            user='root',
                            db='bilibili',
                            charset='utf8mb4',
                            autocommit=True
                            )
    items = ('TagItem', 'CategoryItem', 'VideoItem', 'ArticleItem', 'CommentItem', 'PersonItem')
    transfer = Transfer(mysql, conn, (logger_one.logger, logger_two.logger), items)
    lock = Lock()
    with ThreadPoolExecutor(max_workers=6) as executor:
        executor.map(transfer.transfer, items)

