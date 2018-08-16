# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join
from BilibiliSpider.utils.metrics import *


class DefaultItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class TagItem(scrapy.Item):
    """ 标签
    name: 标签名
    likes: 标签关注数
    publish_nums: 划分到该标签的视频数
    """
    name = scrapy.Field()
    likes = scrapy.Field(input_processor=MapCompose(GetNumber()))
    publish_nums = scrapy.Field(input_processor=MapCompose(GetNumber()))

    def get_insert_sql(self):
        insert_sql = """
            insert into Bili_tag(`name`, `likes`, `publish_nums`) VALUES (%s, %s, %s)
            ON duplicate KEY update `likes`=VALUES (likes), `publish_nums`=VALUES (publish_nums);
        """
        values = (self.get('name'), self.get('likes'), self.get('publish_nums'))
        return insert_sql, values


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
        input_processor=Filter(slice(-1, None)),     # 取从第二个位置开始往后的元素
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
    cover_img_url = scrapy.Field(input_processor=MapCompose(get_cover_img_url))
    title = scrapy.Field()
    desc = scrapy.Field(
        input_processor=MapCompose(strip),
        output_processor=Join("\n")
    )
    url = scrapy.Field()
    img_box = scrapy.Field(output_processor=Join("\n"))
    views = scrapy.Field(input_processor=MapCompose(GetNumber()))
    comments = scrapy.Field(input_processor=MapCompose(GetNumber()))
    coins = scrapy.Field(input_processor=MapCompose(GetNumber()))
    collections = scrapy.Field(input_processor=MapCompose(GetNumber()))
    likes = scrapy.Field(input_processor=MapCompose(GetNumber()))
    shares = scrapy.Field(input_processor=MapCompose(GetNumber()))
    publish_time = scrapy.Field(input_processor=MapCompose(get_date))
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

    def get_insert_sql(self):
        insert_sql = """
            insert into Bili_comment(`sid`, `source`, `person`, `desc`, `likes`, `plat_from`, 
            `reply_person`, `floor`, `is_main`, `publish_time`) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON duplicate KEY update id=(select id from (select id from `Bili_comment` where source=VALUES (source)) res),
             `source`=VALUES (source), `person`=VALUES (person), `likes`=VALUES (likes);
        """
        values = (self.get('sid'), self.get('source'), self.get('person'), self.get('desc'), self.get('likes'), self.get('plat_from'),
                  self.get('reply_person', ""), self.get('floor'), self.get('is_main'), self.get('publish_time'))
        return insert_sql, values


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
    gender = scrapy.Field(input_processor=MapCompose(get_gender))
    sign = scrapy.Field(input_processor=MapCompose(strip))
    uid = scrapy.Field()
    level = scrapy.Field()
    birthday = scrapy.Field(input_processor=MapCompose(get_birthday))
    avatar = scrapy.Field(input_processor=MapCompose(get_avatar))
    attention_nums = scrapy.Field()
    fans_nums = scrapy.Field()
    play_nums = scrapy.Field()
    register_time = scrapy.Field(input_processor=MapCompose(get_date))
    play_game_list = scrapy.Field()
    member_level = scrapy.Field(input_processor=MapCompose(get_member_level))
    tags = scrapy.Field(
        input_processor=MapCompose(strip),
        output_processor=Join(',')
    )

    def get_insert_sql(self):
        insert_sql = """
           insert into Bili_person(`name`, `gender`, `sign`, `uid`, `level`, `birthday`, `avatar`, 
           `attention_nums`, `fans_nums`, `play_nums`, `register_time`, `play_game_list`, `member_level`, `tags`) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           ON duplicate KEY UPDATE `name`=VALUES (name), `gender`=VALUES (gender), `sign`=VALUES (sign),
           `level`=VALUES (`level`), `birthday`=VALUES (birthday), `avatar`=VALUES (avatar)
           `attention_nums`=VALUES (attention_nums), `fans_nums`=VALUES (fans_nums), `play_nums`=VALUES (play_nums)
           `play_game_list`=VALUES (play_game_list), `member_level`=VALUES (member_level), `tags`=VALUES (tags);
       """
        values = (self.get('name'), self.get('gender'), self.get('sign'), self.get('uid'), self.get('birthday'),
                  self.get('avatar'), self.get('attention_nums'), self.get('fans_nums'), self.get('play_nums'),
                  self.get('register_time'), self.get('play_game_list'), self.get('member_level'), self.get('tags'))
        return insert_sql, values
