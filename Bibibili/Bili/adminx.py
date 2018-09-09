# -*- coding:utf-8 -*-
import xadmin
from xadmin import views
from .models import *


class TagAdmin(object):
    list_display = ['tag_id', 'name', 'cover_url', 'likes', 'content', 'publish_nums', 'publish_time']
    search_fields = ['name', 'content']
    list_filter = ['tag_id', 'name', 'cover_url', 'likes', 'content', 'publish_nums', 'publish_time']


class CategoryAdmin(object):
    list_display = ['name', 'code', 'category_type', 'parent', 'publish_nums']
    list_filter = ['name', 'category_type', 'parent']
    search_fields = ['name', 'category_type']


class PersonAdmin(object):
    list_display = ['uid', 'name', 'gender', 'sign', 'level', 'member_level', 'birthday', 'avatar', 'attention_nums',
                    'fans_nums', 'play_nums', 'register_time', 'tags']
    list_filter = ['uid', 'name', 'gender', 'level', 'member_level', 'birthday', 'register_time']
    search_fields = ['uid', 'name', 'gender', 'level', 'member_level', 'birthday', 'register_time']


class VideoAdmin(object):
    list_display = ['vid', 'author', 'title', 'desc', 'url', 'play_nums', 'danmu_nums', 'comments', 'coins',
                    'collections', 'likes', 'shares', 'publish_time', 'tags', 'category']
    list_filter = ['vid', 'author', 'title', 'desc', 'tags', 'publish_time']
    search_fields = ['author', 'title', 'desc', 'play_nums', 'danmu_nums', 'comments',
                     'coins', 'collections', 'likes', 'shares']


class ArticleAdmin(object):
    list_display = ['cid', 'author', 'title', 'desc', 'url', 'cover_img_url', 'img_box', 'views', 'comments', 'coins',
                    'collections', 'likes', 'shares', 'publish_time', 'tags', 'category']
    list_filter = ['vid', 'author', 'title', 'desc', 'tags', 'publish_time']
    search_fields = ['author', 'title', 'desc', 'views', 'comments',
                     'coins', 'collections', 'likes', 'shares']


class CommentAdmin(object):
    list_display = ['sid', 'source', 'person', 'desc', 'likes', 'plat_from', 'reply_person', 'floor',
                    'is_main', 'publish_time', 'type']
    read_only = ['reply_person', 'floor']
    list_filter = ['sid', 'source', 'person', 'desc', 'reply_person', 'is_main', 'likes']
    search_fields = ['sid', 'source', 'person', 'desc', 'reply_person', 'is_main', 'likes']


class BaseSetting(object):
    """基本设置"""
    # 允许主题更换
    enable_themes = True

    # 使用bootstrap主题
    use_bootswatch = True


class GlobalSettings(object):
    site_title = "B站爬虫数据后台"
    site_footer = "BilibiliSpider"
    # menu_style = "accordion"

xadmin.site.register(Tag, TagAdmin)
xadmin.site.register(Category, CategoryAdmin)
xadmin.site.register(Person, PersonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(Article, ArticleAdmin)
xadmin.site.register(Comment, CommentAdmin)
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)