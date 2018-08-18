# -*- coding:utf-8 -*-
from redis import StrictRedis, ConnectionPool
from db_layer.item_map import *
from logs import Logger
from concurrent.futures import ThreadPoolExecutor

import logging
import json
import pymysql



logger_one = Logger(__name__)
logger_two = Logger(__name__)
logger_one.add_file_handler("transfer_failure.log", level=logging.ERROR)
logger_two.add_stream_handler()
logger_two.add_file_handler("transfer_success.log", level=logging.INFO)
pool = ConnectionPool(host='47.106.72.198',
                      password='5762360f',
                      db=0,
                      port=6379
                      )
conn = StrictRedis(connection_pool=pool)
mysql = pymysql.connect(host='47.106.72.198',
                        password='13786836697qwe',
                        port=3306,
                        user='root',
                        db='bilibili',
                        charset='utf8mb4',
                        autocommit=True
                        )
cursor = mysql.cursor()


class Transfer(object):
    def __init__(self, mysql, redis, loggers, items, chunk_size=10):
        self.mysql = mysql
        self.redis = redis
        self.items = items
        self.loggers = loggers
        self.chunk_size = chunk_size
        self.base_key = "bilibili:%(item)s"

    def transfer(self, item):
        while True:
            key = self.base_key % {'item': item}
            key_len = self.redis.llen(key)
            if key_len:
                chunk_size = self.chunk_size if self.chunk_size > key_len else key_len
                item_cls = eval(item)
                for _ in range(chunk_size):
                    try:
                        data = item_cls(json.loads(self.redis.lpop(key), encoding='utf8'))
                    except Exception as e:
                        self.handle_info(item, "None", e)
                    self._transfer(item, data)

    def _transfer(self, item, data):
        insert_sql, params = data.get_insert_sql()
        try:
            self.mysql.execute(insert_sql, params)
        except Exception as e:
            self.handle_exception(item, data, e)
        else:
            self.handle_info(item, data)

    def handle_exception(self, item, data, exception):
        self.loggers[1].error(item + ": " + str(data) + str(exception))

    def handle_info(self, item, data):
        self.loggers[0].info(item + ": " + str(data))


if __name__ == '__main__':
    items = ('TagItem', 'CategoryItem', 'VideoItem', 'ArticleItem', 'CommentItem', 'PersonItem')
    transfer = Transfer(cursor, conn, (logger_one.logger, logger_two.logger), items)
    with ThreadPoolExecutor() as executor:
        executor.map(transfer.transfer, items)

