# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join
from elasticsearch_dsl import connections
from BilibiliSpider.models import ArticleDocType, TagDocType, CommentDocType, VideoDocType, PersonDocType
from BilibiliSpider.utils.metrics import *

# 创建es连接
es = connections.create_connection(ArticleDocType._doc_type.using)


class DefaultItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class TagItem(scrapy.Item):
    """ 标签
    name: 标签名
    likes: 标签关注数
    publish_nums: 划分到该标签的视频数
    """
    tag_id = scrapy.Field()
    cover_url = scrapy.Field()
    name = scrapy.Field()
    content = scrapy.Field()
    likes = scrapy.Field()
    publish_time = scrapy.Field(input_processor=MapCompose(from_timestamp))
    publish_nums = scrapy.Field(input_processor=MapCompose(GetNumber()))

    def get_insert_sql(self):
        insert_sql = """
            insert into Bili_tag(`tag_id`,`cover_url`, `name`, `content`, `likes`, `publish_time`, `publish_nums`)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON duplicate KEY update `likes`=VALUES (likes), `publish_nums`=VALUES (publish_nums)
            `content`=VALUES (content), `cover_url`=VALUES (cover_url);
        """
        values = (self.get('tag_id'), self.get('cover_url'), self.get('name'), self.get('content'),
                  self.get('likes'), self.get('publish_time'), self.get('publish_nums'))
        return insert_sql, values

    def save_to_es(self):
        tag = TagDocType()
        tag.suggest = gen_suggests(TagDocType._doc_type.index, ((tag.name, 10), (tag.content, 8)))
        tag.tag_id = self.get('tag_id')
        tag.cover_url = self.get('cover_url', "")
        tag.name = self.get('name')
        tag.content = self.get('content')
        tag.likes = self.get('likes')
        tag.publish_time = self.get('publish_time')
        tag.publish_nums = self.get('publish_nums')
        tag.save()


class CategoryItem(scrapy.Item):
    """ 分类
    name: 分类名
    category_type: 分类等级
    parent: 父级分类
    publish_nums: 该分类下的投稿数
    """
    name = scrapy.Field()
    category_type = scrapy.Field()
    parent = scrapy.Field()
    publish_nums = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into Bili_category(`name`, `category_type`, `parent_id`, `publish_nums`) 
            VALUES (%s, %s, %s, %s)
            ON duplicate KEY UPDATE `category_type`=VALUES (category_type),
            `parent_id`=VALUES (parent_id), `publish_nums`=VALUES (publish_nums)
        """
        values = (self.get('name'), self.get('category_type'),
                  self.get('parent'), self.get('publish_nums'))
        return insert_sql, values


class VideoItem(scrapy.Item):
    """ 视频
    vid: 视频id
    author: up主
    title: 标题
    desc: 描述
    url: 链接地址
    play_nums: 播放数
    danmu_nums: 弹幕数
    comments: 评论数
    coins: 硬币数
    collections: 收藏数
    shares: 分享数
    likes: 点赞数
    publish_time: 发布日期
    category: 分类
    tags: 标签
    """
    vid = scrapy.Field()
    author = scrapy.Field()
    title = scrapy.Field()
    desc = scrapy.Field(
        input_processor=MapCompose(remove_tags, strip),
        output_processor=Join("\n")
    )
    url = scrapy.Field()
    play_nums = scrapy.Field()
    danmu_nums = scrapy.Field()
    comments = scrapy.Field()
    coins = scrapy.Field()
    collections = scrapy.Field()
    likes = scrapy.Field()
    shares = scrapy.Field()
    publish_time = scrapy.Field(input_processor=MapCompose(get_datetime))
    category = scrapy.Field(
        input_processor=Filter(slice(-1, None)),  # 取从第二个位置开始往后的元素
        output_processor=Join(',')
    )
    tags = scrapy.Field(output_processor=Join(','))

    def get_insert_sql(self):
        insert_sql = """
            insert into Bili_video(`vid`, `author`, `title`, `desc`, `url`, `play_nums`, `danmu_nums`, 
            `comments`, `coins`, `collections`, `likes`, `shares`, `publish_time`, `category`, `tags`) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            on duplicate key update 
            `author`=VALUES (author), `title`=VALUES (title), `desc`=VALUES (`desc`), `play_nums`=VALUES (play_nums),
            `danmu_nums`=VALUES (danmu_nums), `comments`=VALUES (comments), `coins`=VALUES (coins), 
            `collections`=VALUES (collections), `likes`=VALUES (likes), `shares`=VALUES (shares), 
            `category`=VALUES (category), `tags`=VALUES (tags); 
        """
        values = (self.get('vid'), self.get('author'), self.get('title'), self.get('desc'), self.get('url'), self.get('play_nums'),
                  self.get('danmu_nums'), self.get('comments'), self.get('coins'), self.get('collections'),
                  self.get('likes'), self.get('shares'), self.get('publish_time'), self.get('category'), self.get('tags'))
        return insert_sql, values

    def save_to_es(self):
        video = VideoDocType()
        video.vid = self.get('vid')
        video.author = self.get('author')
        video.title = self.get('title')
        video.desc = self.get('desc')
        video.url = self.get('url')
        video.play_nums = self.get('play_nums')
        video.danmu_nums = self.get('danmu_nums')
        video.comments = self.get('comments')
        video.coins = self.get('coins')
        video.collections = self.get('collections')
        video.likes = self.get('likes')
        video.shares = self.get('shares')
        video.publish_time = self.get('publish_time')
        video.category = self.get('category')
        video.tags = self.get('tags')
        video.suggest = gen_suggests(video._doc_type.index, ((video.title, 10),
                                                             (video.desc, 8),
                                                             (video.category, 6),
                                                             (video.tags, 4),
                                                             (video.author, 3)))
        video.save()


class ArticleItem(scrapy.Item):
    """ 文章
    cid: 文章id
    author: up主
    cover_img_url: 封面地址
    title: 标题
    desc: 描述
    url: 链接地址
    img_box: 图源箱
    views: 阅读数
    comments: 评论数
    coins: 硬币数
    collections: 收藏数
    shares: 分享数
    likes: 点赞数
    publish_time: 发布日期
    category: 分类
    tags: 标签
    """
    cid = scrapy.Field()
    author = scrapy.Field()
    cover_img_url = scrapy.Field()
    title = scrapy.Field()
    desc = scrapy.Field(
        input_processor=MapCompose(strip),
        output_processor=Join("\n")
    )
    url = scrapy.Field()
    img_box = scrapy.Field(output_processor=Join("\n"))
    views = scrapy.Field()
    comments = scrapy.Field()
    coins = scrapy.Field()
    collections = scrapy.Field()
    likes = scrapy.Field()
    shares = scrapy.Field()
    publish_time = scrapy.Field(
        input_processor=MapCompose(lambda x: datetime.fromtimestamp(int(x)))
    )
    category = scrapy.Field()
    tags = scrapy.Field(output_processor=Join(','))

    def get_insert_sql(self):
        insert_sql = """
            insert into Bili_article(`cid`, `author`, `cover_img_url`, `title`, `desc`, `url`, `img_box`, `views`, 
            `comments`, `coins`, `collections`, `likes`, `shares`, `publish_time`, `category`, `tags`) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            on duplicate key UPDATE 
            `author`=VALUES (author), `cover_img_url`=VALUES (cover_img_url), `title`=VALUES (title), 
            `desc`=VALUES (`desc`), `img_box`=VALUES (img_box),
            `views`=VALUES (views), `comments`=VALUES (comments), `coins`=VALUES (coins), 
            `collections`=VALUES (collections), `likes`=VALUES (likes), `shares`=VALUES (shares), 
            `category`=VALUES (category), `tags`=VALUES (tags);
        """
        values = (self.get('cid'), self.get('author'), self.get('cover_img_url'), self.get('title'), self.get('desc'), self.get('url'),
                  self.get('img_box'), self.get('views'), self.get('comments'), self.get('coins'), self.get('collections'),
                  self.get('likes'), self.get('shares'), self.get('publish_time'), self.get('category'), self.get('tags'))
        return insert_sql, values

    def save_to_es(self):
        article = ArticleDocType()
        article.cid = self.get('cid')
        article.author = self.get('author')
        article.title = self.get('title')
        article.desc = self.get('desc')
        article.url = self.get('url')
        article.views = self.get('views')
        article.comments = self.get('comments')
        article.coins = self.get('coins')
        article.collections = self.get('collections')
        article.likes = self.get('likes')
        article.shares = self.get('shares')
        article.publish_time = self.get('publish_time')
        article.category = self.get('category')
        article.tags = self.get('tags')
        article.suggest = gen_suggests(article._doc_type.index, ((article.title, 10),
                                                                 (article.desc, 8),
                                                                 (article.category, 6),
                                                                 (article.tags, 4),
                                                                 (article.author, 3)))
        article.save()


class CommentItem(scrapy.Item):
    """ 评论
    sid: 来源aid, cid
    source: 来源
    person: 评论用户
    desc: 评论描述
    likes: 点赞数
    plat_from: 平台
    reply_person: 被回复人
    floor: 楼层数
    is_main: 是否主楼
    publish_time: 发布时间
    """
    sid = scrapy.Field()
    source = scrapy.Field()
    person = scrapy.Field()
    desc = scrapy.Field()
    likes = scrapy.Field()
    plat_from = scrapy.Field()
    reply_person = scrapy.Field()
    floor = scrapy.Field()
    is_main = scrapy.Field()
    publish_time = scrapy.Field()
    type = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into Bili_comment(`sid`, `source`, `person`, `desc`, `likes`, `plat_from`, 
            `reply_person`, `floor`, `is_main`, `publish_time`, `type`) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON duplicate KEY update `source`=VALUES (source), `person`=VALUES (person), `likes`=VALUES (likes);
        """
        values = (self.get('sid'), self.get('source'), self.get('person'), self.get('desc'), self.get('likes'), self.get('plat_from'),
                  self.get('reply_person', ""), self.get('floor'), self.get('is_main'), self.get('publish_time'), self.get('type'))
        return insert_sql, values

    def save_to_es(self):
        comment = CommentDocType()
        comment.sid = self.get('sid')
        comment.source = self.get('source')
        comment.person = self.get('person')
        comment.desc = self.get('desc')
        comment.likes = self.get('likes')
        comment.reply_person = self.get('reply_person')
        comment.floor = self.get('floor')
        comment.publish_time = self.get('publish_time')
        comment.suggest = gen_suggests(comment._doc_type.index, ((comment.desc, 10), (comment.person, 7), (comment.reply_person, 5)))
        comment.save()


class PersonItem(scrapy.Item):
    """ 用户
    name: 用户名
    sex: 性别
    sign: 签名
    uid: uid
    level: b站等级
    birthday: 生日
    avatar: 头像
    attention_nums: 关注数
    fence_nums: 粉丝数
    play_game_list: 最近玩过的游戏
    member_level: 会员等级
    subscribe_tags: 订阅标签
    """
    name = scrapy.Field()
    gender = scrapy.Field()
    sign = scrapy.Field(input_processor=MapCompose(strip))
    uid = scrapy.Field()
    level = scrapy.Field()
    birthday = scrapy.Field(input_processor=MapCompose(get_birthday))
    avatar = scrapy.Field()
    attention_nums = scrapy.Field()
    fans_nums = scrapy.Field()
    play_nums = scrapy.Field()
    register_time = scrapy.Field(input_processor=MapCompose(from_timestamp))
    member_level = scrapy.Field()
    tags = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
           insert into Bili_person(`name`, `gender`, `sign`, `uid`, `level`, `birthday`, `avatar`, 
           `attention_nums`, `fans_nums`, `play_nums`, `register_time`, `member_level`, `tags`) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           ON duplicate KEY UPDATE `name`=VALUES (name), `gender`=VALUES (gender), `sign`=VALUES (sign),
           `level`=VALUES (`level`), `birthday`=VALUES (birthday), `avatar`=VALUES (avatar)
           `attention_nums`=VALUES (attention_nums), `fans_nums`=VALUES (fans_nums), `play_nums`=VALUES (play_nums)
           `member_level`=VALUES (member_level), `tags`=VALUES (tags);
       """
        values = (self.get('name'), self.get('gender'), self.get('sign'), self.get('uid'), self.get('birthday'),
                  self.get('avatar'), self.get('attention_nums'), self.get('fans_nums'), self.get('play_nums'),
                  self.get('register_time'), self.get('member_level'), self.get('tags'))
        return insert_sql, values

    def save_to_es(self):
        person = PersonDocType()
        person.name = self.get("name")
        person.sign = self.get("sign")
        person.uid = self.get("uid")
        person.birthday = self.get("birthday")
        person.avatar = self.get("avatar")
        person.attention_nums = self.get("attention_nums")
        person.fans_nums = self.get("fans_nums")
        person.play_nums = self.get("play_nums")
        person.register_time = self.get("register_time")
        person.tags = self.get("tags")
        person.suggest = gen_suggests(person._doc_type.index, ((person.name, 10), (person.sign, 7), (person.uid, 4), (person.tags, 2)))


class OnlineItem(scrapy.Item):
    all_count = scrapy.Field()
    web_online = scrapy.Field()
    play_online = scrapy.Field()
    current_time = scrapy.Field()


def gen_suggests(index, info_tuple):
    """根据字符串生成搜索建议数组(ES)
    :param index: ElasticSearch索引
    :param info_tuple: 信息权重元组
    """
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            # 调用es的analyzer接口分析字符串, words拿到分析得到的token
            words = es.indices.analyze(index=index, params={'analyzer': 'ik_max_word', 'filter': ["lowercase"]}, body=text)
            # 从token中得到所有由analyzer分析得到的分词
            analyzed_words = set([r["token"] for r in words["tokens"] if len(r['token']) > 1])
            # 得到所有未使用的分词
            new_words = analyzed_words - used_words  # 差集
        else:
            new_words = set()

        if new_words:
            suggests.append({"input": list(new_words), "weight": weight})
    return suggests
