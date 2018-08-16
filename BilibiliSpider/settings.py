# -*- coding: utf-8 -*-
import os 
import sys

BOT_NAME = 'KoiSato'

SPIDER_MODULES = ['BilibiliSpider.spiders']
NEWSPIDER_MODULE = 'BilibiliSpider.spiders'

# 使用scrapy-redis的scheduler
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# 使用scrapy-redis的过滤器
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# REDIS_ITEMS_SERIALIZER = 'json.dumps'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# 启用cookie
COOKIES_ENABLED = True

DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en',
}

# Spider中间件, 控制spider接受response与产出item的行为
SPIDER_MIDDLEWARES = {
   'BilibiliSpider.middlewares.BilibilispiderSpiderMiddleware': 543,
}

# 下载器中间件, 轻量中间处理器
DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 200,
    'BilibiliSpider.middlewares.RandomUserAgentMiddleware': 250,
    'BilibiliSpider.middlewares.RandomProxyMiddleware': 300,
    'BilibiliSpider.middlewares.DynamicRefererMiddleware': 350,
    'BilibiliSpider.middlewares.PosturlParseMiddleware': 150,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,     # 禁用默认的UserAgent
    # 'BilibiliSpider.middlewares.SeleniumDownloadMiddleware': 543,         # 使用selenium爬取模式开启
}

# 扩展
EXTENSIONS = {
    'BilibiliSpider.extensions.GetRemotePasswordExtension': 200,            # get远程连接密码
    # 'BilibiliSpider.extensions.ParseOnlineExtension': 300                   # 在线人数抓取
}

ITEM_PIPELINES = {
    'BilibiliSpider.pipelines.RedisPipeline': 300,                    # redis管道
    'BilibiliSpider.pipelines.MysqlTwistPipeline': 200,               # mysql异步管道
    # 'BilibiliSpider.pipelines.JsonExporterPipeline': 250              # json管道
}

# 并发设置
CONCURRENT_REQUESTS = 10
CONCURRENT_REQUESTS_PER_DOMAIN = 10

# 根目录搜索设置
BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
ROOT_DIR = os.path.join(BASE_DIR, 'BilibiliSpider')
sys.path.insert(0, ROOT_DIR)

# Fake_User-Agent
RANDOM_UA_TYPE = "random"

# Local Database
MYSQL_HOST = '127.0.0.1'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'
MYSQL_PORT = 3306
MYSQL_DATABASE = 'learning'
MYSQL_CHARSET = 'utf8'
MYSQL_ACDB = 'sys'

# The SECRET_KEY to get remote db's account
ID = 7
SECRET_KEY = "3550d4cf80e963a6c484c96c960349da"

# Remote Mysql DB
REMOTE_MYSQL_HOST = '47.106.72.198'
REMOTE_MYSQL_PORT = 3306
REMOTE_MYSQL_DATABASE = 'bilibili'
REMOTE_MYSQL_CHARSET = 'utf8'
REMOTE_MYSQL_TOOLDB = 'tools'

# Remote Redis DB
REDIS_HOST = '47.106.72.198'
REDIS_PORT = 6379
REDIS_PARAMS = {
    'password': '5762360f'
}

# output - format
SQL_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
SQL_DATE_FORMAT = "%Y-%m-%d"
SQL_FILEDATE_FORMAT = '%Y/%m/%d'

# 图片下载设置
IMAGES_STORE = os.path.join(ROOT_DIR, 'images')     # 存储图片的地址
IMAGES_URLS_FIELD = 'img_urls'                      # items中的下载图片的地址字段
IMAGES_DIRECTORY_NAME = 'default'

# JSON EXPORT SETTINGS
JSON_FILE_NAME = 'bilibili.json'                    # json文件名
JSON_EXPORT_LOCATION = os.path.join(ROOT_DIR, 'exports')    # json保存文件夹

# PIPELINE of ITEM (选择管道产出相应的item)
JSON_ITEMS = ('OnlineItem',)
MYSQL_ITEMS = ('TagItem', 'CategoryItem', 'VideoItem', 'ArticleItem', 'CommentItem', 'PersonItem')
REDIS_ITEMS = ('OnlineItem',)

# 在线人数爬取时间间隔设置
# 每120s爬取一次
ONLINE_INTERVAL = 120

# 爬取页面设置
PARSE_DETAIL_ORDER_ASC = True           # True 顺序爬取, False 反向爬取
PARSE_COMMENTS = True                   # 是否爬取评论
PARSE_COMMENTS_MAX_PAGES = 50           # 最大评论爬取页数, 每页50个评论
PARSE_CHILD_COMMENTS = True             # 是否爬取子评论
PARSE_CHILD_COMMENTS_MAX_PAGES = 50     # 子评论爬取页数

# SCHEDULER_FLUSH_ON_START = True


# cookie是否来自文件
COOKIES_FROM_FILE = True

# 为False将接受以下参数
# 可以接受字符形式的原始cookie数据
COOKIES_STRING = """

"""

# 也可接受字典形式的cookie数据
COOKIES_DICT = {

}