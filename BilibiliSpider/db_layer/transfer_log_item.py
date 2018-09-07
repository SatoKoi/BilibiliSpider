# -*- coding:utf-8 -*-
import re
import os
import sys
import pymysql

base_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, base_dir)

from db_layer.logs import *
from db_layer.item_map import *
from threading import Lock


class LogTransfer(object):
    def __init__(self, mysql, loggers, items, file):
        self.mysql = mysql
        self.items = items
        self.loggers = loggers
        self.file = file

    def parse_log_file(self):
        with open(self.file, 'r', encoding='utf8') as f:
            data = ""
            with self.mysql.cursor() as cursor:
                while True:
                    data += f.readline().strip('\n')
                    if re.search(r'__main__', data, re.M):
                        self._parse_raw_text(cursor, data)
                        data = ""
                    elif not data:
                        break

    def _parse_raw_text(self, cursor, data):
        for item in self.items:
            if re.search(item, data, re.I):
                result = re.search(r'({.*})', data)
                decode_data = eval(result.group(1))
                item_cls = eval(item)
                try:
                    data = item_cls(decode_data)
                except Exception as e:
                    for _item in self.items:
                        try:
                            item_cls = eval(_item)
                            data = item_cls(decode_data)
                            self._transfer(cursor, item, data)
                            return
                        except:
                            pass
                    self.handle_exception(item, data, e)
                else:
                    self._transfer(cursor, item, data)
                    return

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
        self.loggers[1].error(item + ": " + str(data) + str(exception))

    def handle_info(self, item, data):
        self.loggers[0].info(item + ": " + str(data))


if __name__ == '__main__':
    logger_one = Logger(__name__)
    logger_two = Logger(__name__)
    logger_one.add_file_handler("transfer_log_failure.log", level=logging.ERROR)
    logger_two.add_stream_handler()
    logger_two.add_file_handler("transfer_log_success.log", level=logging.INFO)
    mysql = pymysql.connect(host='47.106.72.198',
                            password='13786836697qwe',
                            port=3306,
                            user='root',
                            db='bilibili',
                            charset='utf8mb4',
                            autocommit=True
                            )
    items = ('TagItem', 'CategoryItem', 'VideoItem', 'ArticleItem', 'CommentItem', 'PersonItem')
    lock = Lock()
    transfer = LogTransfer(mysql, (logger_one.logger, logger_two.logger), items, './transfer_failure.log')
    transfer.parse_log_file()