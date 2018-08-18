# -*- coding:utf-8 -*-
import pprint


class DictItem(object):
    __slots__ = ("d")

    def __init__(self, d):
        self.d = d

    def __getitem__(self, item):
        return self.d[item]

    def get(self, key, default=None):
        return self.d.get(key, default)

    def start_pretty(self):
        return "{\n"

    def finish_pretty(self):
        return "}"

    def pretty_value(self, value):
        if isinstance(value, str):
            return '"{}"'.format(value)
        return str(value)

    def pretty_key(self, key):
        return '"{}"'.format(key)

    def __str__(self):
        string = self.start_pretty()
        indent = 4
        for k, v in self.d.items():
            string += indent * " " + self.pretty_key(k) + ': ' + self.pretty_value(v) + ",\n"
        return string + self.finish_pretty()


class TagItem(DictItem):
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


class VideoItem(DictItem):
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


class ArticleItem(DictItem):
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


class CommentItem(DictItem):
    def get_insert_sql(self):
        insert_sql = """
            insert into Bili_comment(`sid`, `source`, `person`, `desc`, `likes`, `plat_from`, 
            `reply_person`, `floor`, `is_main`, `publish_time`, `type`) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON duplicate KEY UPDATE 
             `source`=VALUES (source), `person`=VALUES (person), `likes`=VALUES (likes);
        """
        values = (self.get('sid'), self.get('source'), self.get('person'), self.get('desc'), self.get('likes'), self.get('plat_from'),
                  self.get('reply_person', ""), self.get('floor'), self.get('is_main'), self.get('publish_time'), self.get('type'))
        return insert_sql, values


class PersonItem(DictItem):
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