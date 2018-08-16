# -*- coding:utf-8 -*-
import scrapy
import json

from scrapy.signals import spider_error
from scrapy.xlib.pydispatch import dispatcher

from .settings import COOKIES_DICT, COOKIES_STRING, COOKIES_FROM_FILE


class ReplyMixin(object):

    def reply(self, response):
        data = json.loads(response.text)
        formdata = {
            'oid': '',
            'type': '1',
            'message': '',
            'plat': '1',
            'csrf': self.csrf,
            'jsonp': 'jsonp'
        }
        formdata.update(data)
        try:
            check_data(data)
        except ValueError:
            dispatcher.connect(self.handle_exception, signal=spider_error)
        yield scrapy.FormRequest(url=self.api_urls.get("postreply"),
                                 cookies=self.cookies,
                                 formdata=formdata,
                                 callback=self.check_status,
                                 dont_filter=True)


class GetCookieMixin(object):
    def get_cookies(self):
        cookie_dict = {}
        if COOKIES_FROM_FILE:
            for dirpath, dirname, files in os.walk('BilibiliSpider/cookie'):
                for f in files:
                    with open(os.path.join(dirpath, f), 'r') as f_obj:
                        cookie_dict.update({f: f_obj.read()})
        else:
            if COOKIES_STRING:
                cookie_dict = cookies_from_string(COOKIES_STRING)
            if COOKIES_DICT:
                cookie_dict = COOKIES_DICT
        return cookie_dict


def check_data(data):
    for k, v in data.items():
        if not v:
            raise ValueError("{} needs a not null value".format(k))