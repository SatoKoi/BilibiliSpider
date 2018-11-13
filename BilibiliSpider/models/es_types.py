# -*- coding:utf-8 -*-
__author__ = 'KoiSato'

from elasticsearch_dsl import DocType, Completion, Text, Keyword, Integer, Date
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=["localhost"])


class CustomAnalyzer(_CustomAnalyzer):
    """避免报错"""

    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=['lowercase'])  # 分词分析器


class SuggestField(object):
    suggest = Completion(analyzer=ik_analyzer)


class ActicleDocType(SuggestField, DocType):
    cid = Integer()
    author = Text(analyzer="ik_max_word")
    cover_img_url = Keyword()
    title = Text(analyzer="ik_max_word")
    desc = Text(analyzer="ik_max_word")
    url = Keyword()
    views = Integer()
    comments = Integer()
    coins = Integer()
    collections = Integer()
    likes = Integer()
    shares = Integer()
    publish_time = Date()
    category = Text(analyzer="ik_max_word")
    tags = Text(analyzer="ik_max_word")


class VideoDocType(SuggestField, DocType):
    vid = Integer()
    author = Text(analyzer="ik_max_word")
    title = Text(analyzer="ik_max_word")
    desc = Text(analyzer="ik_max_word")
    url = Keyword()
    play_nums = Integer()
    danmu_nums = Integer()
    comments = Integer()
    coins = Integer()
    collections = Integer()
    likes = Integer()
    shares = Integer()
    publish_time = Date()
    category = Text(analyzer="ik_max_word")
    tags = Text(analyzer="ik_max_word")


class CommentDocType(SuggestField, DocType):
    sid = Integer()
    source = Keyword()
    person = Text(analyzer="ik_max_word")
    desc = Text(analyzer="ik_max_word")
    likes = Integer()
    reply_person = Text(analyzer="ik_max_word")
    floor = Integer()
    publish_time = Date()


class TagDocType(SuggestField, DocType):
    tag_id = Integer()
    cover_url = Keyword()
    name = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")
    likes = Integer()
    publish_time = Date()
    publish_nums = Integer()


class PersonDocType(SuggestField, DocType):
    name = Text(analyzer="ik_max_word")
    sign = Text(analyzer="ik_max_word")
    uid = Integer()
    birthday = Date()
    avatar = Keyword()
    attention_nums = Integer()
    fans_nums = Integer()
    play_nums = Integer()
    register_time = Date()
    tags = Text(analyzer="ik_max_word")


if __name__ == '__main__':
    ActicleDocType.init()
    VideoDocType.init()
    CommentDocType.init()
    TagDocType.init()
    PersonDocType.init()