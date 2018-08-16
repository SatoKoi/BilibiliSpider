# -*- coding:utf-8 -*-
from datetime import datetime, date, timedelta
from urllib.parse import urljoin, urlparse
from array import array
from numbers import Integral
from collections import Sized
from w3lib.html import remove_tags as rm_tags
from lxml import etree
from ..settings import SQL_DATETIME_FORMAT
import re


def map_category(mapping, source):
    """category映射"""
    for k in mapping.keys():
        try:
            idx = source.index(k)
            if idx >= 0:
                return mapping[k].get('id')
        except ValueError:
            pass
    return None


def get_gender(x):
    """
    get gender
    :param x: str
    :return: 0 -> secret, 1 -> male, 2 -> female
    """
    genders = ["male", "female"]
    for gender in genders:
        idx = 1
        try:
            x.index(gender)
            return idx
        except Exception:
            idx += 1
    return 0


def strip(x):
    """
    x.strip()
    :param x: str
    :return: x.strip()
    """
    return str(x).strip()


def get_date(x):
    """
    get datetime
    :param x: str
    :return: datetime obj
    """
    res = re.search(r"(\d+)-(\d+)-(\d+)", x, re.MULTILINE)
    if res:
        x = res.group(0)
        date_time = datetime.strptime(x, "%Y-%m-%d")
    else:
        date_time = datetime.now()
    return date_time


def get_datetime(x):
    try:
        return datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
    except:
        return datetime.now()


def get_member_level(x):
    """
    get member level
    :param x: str
    :return: 0 -> normal, 1 -> normal-v, 2 -> annual-v
    """
    levels = ['normal-v', 'annual-v']
    for level in levels:
        idx = 1
        try:
            x.index(level)
            return idx
        except Exception:
            idx += 1
    return 0


def get_birthday(x):
    """
    get birthday
    :param x: str
    :return: date obj
    """
    res = re.search(r"(\d+)-(\d+)", str(x), re.MULTILINE)
    if res:
        birth = date(year=datetime.now().year, month=int(res.group(1)), day=int(res.group(2)))
    else:
        birth = date(year=datetime.now().year)
    return birth


def get_avatar(x):
    """
    get avatar url
    :param x: str
    :return: urljoin(str)
    """
    return str(x).replace('/', '', 2)


def get_cover_img_url(x):
    """
    get cover image url
    :param x: str
    :return: match group()
    """
    res = re.search(r'(https://(.*?)")', x, re.M)
    if res:
        return res.group()
    return x


def remove_tags(x):
    return rm_tags(x, encoding='utf8')


def createDatetime(x):
    """
    create datetime obj
    :param x: str
    :return: correct datetime obj
    """
    try:
        x = strip(x)
        return datetime.strptime(x, "%Y-%m-%d %H:%M")
    except Exception:
        now = datetime.now()
        res = re.search(r'(\d+)小时', x, re.M)
        if res:
            hour = int(res.group(1))
            dtl = timedelta(hours=hour)
            return datetime(year=now.year, month=now.month, day=now.day, hour=now.hour) - dtl
        res = re.search(r'(\d+)分', x, re.M)
        if res:
            minute = int(res.group(1))
            dtl = timedelta(minutes=minute)
            return datetime(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute) - dtl
        res = re.search(r'(\d+)秒', x, re.M)
        if res:
            second = int(res.group(1))
            dtl = timedelta(seconds=second)
            return datetime(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute, second=now.second) - dtl
    return datetime.now()


def find_reply_person(x):
    """
    查找楼层回复
    :param x: str
    :return: reply_person, reply_content
    """
    res = re.search(r'@(\w+)\s*:(.*)', strip(x), re.M)
    if res:
        return res.group(1), res.group(2)
    return "", x


def get_id(x):
    """
    get url source id
    :param x: str
    :return: source id
    """
    res = re.search(r'[ac]v(\d+)', x, re.M)
    return int(res.group(1)) if res else 0


def get_source(x):
    """
    get url source
    :param x: str
    :return: source
    """
    res = re.search(r'[ac]v(\d+)', x, re.M)
    return res.group(0) if res else None


def get_plat(x):
    return x if x <= 3 else 4


def get_type(x):
    if re.search(r'av\d+', str(x)):
        return 0
    elif re.search(r'cv\d+', str(x)):
        return 1


def from_timestamp(x):
    return datetime.fromtimestamp(int(x))


def cookies_from_string(x):
    cookie_dict = {}
    for cookie in str(x).split("; "):
        r = cookie.split('=')
        cookie_dict.update({r[0]: r[1]})
    return cookie_dict


class GetNumber(object):
    """对于一组字符串, 只获取其中的数字"""
    def __init__(self, count=1, default=0):
        """
        :param count: 获取字符串分离的数字次数
        :param default: 当获取不到数字时默认的返回结果
        """
        assert isinstance(count, Integral) and isinstance(default, Integral),\
            "count and default must be a int type"
        self.count = count
        self.default = default

    def __call__(self, value):
        result = array('i')
        count = 0
        for value in re.findall(r'(\d+)', value, re.M):
            count += 1
            if count <= self.count:
                try:
                    result.append(int(value))
                except:
                    pass
        if count == 0:
            result.append(self.default)
        return result


class Filter(object):
    def __init__(self, index=-1):
        if isinstance(index, Integral) or \
                isinstance(index, Sized) or \
                isinstance(index, slice):
            self.index = index
        else:
            raise TypeError("The Filter instance require a slice index "
                            "which types must between a int and a slice object")

    def __call__(self, value):
        """
        :param value: list
        :return: list
        """
        assert isinstance(value, Sized), "value must be a slice object"
        if isinstance(self.index, Integral):
            return [value[self.index]]
        if isinstance(self.index, slice):
            return value[self.index]
        result = []
        for index in self.index:
            try:
                result.append(value[index])
            except IndexError as e:
                print(e)
        return result
