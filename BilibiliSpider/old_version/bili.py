# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin, urlparse

import pyquery
import scrapy
from BilibiliSpider.items import DefaultItemLoader, CategoryItem, CommentItem, PersonItem, TagItem, VideoItem, ArticleItem
from BilibiliSpider.map.defaults import *
from BilibiliSpider.scripts import Script
from BilibiliSpider.settings import *
from BilibiliSpider.utils.metrics import map_category, createDatetime, GetNumber, find_reply_person, get_id, get_source
from scrapy import signals
from scrapy.linkextractors import LinkExtractor
from scrapy.spider import Rule
from scrapy.xlib.pydispatch import dispatcher
from scrapy_redis.spiders import RedisCrawlSpider
from selenium.webdriver import Chrome, ChromeOptions


class BiliSpider(RedisCrawlSpider):
    """基于Redis的可持续化爬虫"""
    name = 'bili'
    allowed_domains = ['www.bilibili.com', 'space.bilibili.com']
    base_url = "https://www.bilibili.com/"
    # start_urls = ['https://www.bilibili.com/']
    redis_key = "bilibili:request_urls"

    custom_settings = {
        'COOKIES_ENABLED': True,
        'DOWNLOADER_DELAY': 0.5,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'www.bilibili.com',
            'Origin': 'https://www.bilibili.com',
            'Referer': 'https://www.bilibili.com/',
        }
    }

    # firefox_options = FirefoxOptions()
    # firefox_options.add_argument('--headless')

    chrome_options = ChromeOptions()
    # chrome_options.set_headless()     # 设置无窗口爬虫模式
    # chrome_options.add_argument('window-size=1920x3000')  # 指定浏览器分辨率
    # chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    # chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
    # chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
    # chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败

    rules = (
        Rule(LinkExtractor(allow=(r'v/(\w+)/(\w+)/#/all/default/(\d/\d+)*',)), callback='parse_page', follow=True),
        Rule(LinkExtractor(allow=(r'v/(\w+)/(\w+)/',)), callback='parse_category', follow=True),
        Rule(LinkExtractor(allow=(r'video/av(\d+)/',)), callback='parse_detail', follow=True),
        Rule(LinkExtractor(allow=(r'(\d+)/',), allow_domains='space.bilibili.com/'), callback='parse_person', follow=True),
        Rule(LinkExtractor(allow=(r'read/cv(\d+)/',)), callback='parse_article', follow=True),
        Rule(LinkExtractor(allow=(r'tag/(\d+)/(.*)',)), callback='parse_tags', follow=True),
    )

    handle_httpstatus_list = [404]

    def __init__(self, *args, **kwargs):
        # 设置chrome不加载图片
        # self.chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        self.browser = Chrome(executable_path="F:\ChromeDriver\chromedriver.exe", chrome_options=self.chrome_options)
        # self.browser = Firefox(firefox_options=self.firefox_options)
        # self.webdriver_pool = WebdriverPool(CONCURRENT_REQUESTS, "chrome", self.chrome_options)
        # self.queue = self.webdriver_pool.queue
        self.script = Script()
        self.parse_partial = reversed if PARSE_DETAIL_ORDER_ASC else lambda x: x
        # self.phantom_js = PhantomJS(executable_path="F:\phantomjs-2.1.1-windows\\bin\phantomjs.exe")
        self.reg_pattern = REG_PATTERN
        self.get_two = GetNumber(2)
        dispatcher.connect(self.handle_spider_closed, signals.spider_closed)
        super(BiliSpider, self).__init__(*args, **kwargs)

    def parse_start_url(self, response, **kwargs):
        """对于起始url的爬取规则添加回调"""
        parse_res = urlparse(response.url)
        if re.match(self.reg_pattern['video'], parse_res.path, re.I):
            return self.parse_detail(response)
        if re.match(self.reg_pattern['user'], parse_res.path, re.I)\
                and parse_res.netloc == self.allowed_domains[1]:
            return self.parse_person(response)
        if re.match(self.reg_pattern['article'], parse_res.path, re.I):
            return self.parse_article(response)
        if re.match(self.reg_pattern['tag'], parse_res.path, re.I):
            return self.parse_tags(response)
        return []

    def parse_category(self, response):
        """解析分类页"""
        category_loader = DefaultItemLoader(item=CategoryItem(), response=response)
        category_loader.add_value('name', response.meta['link_text'])
        category_loader.add_value('parent', map_category(CATEGORY_MAP, response.url))
        category_loader.add_value('category_type', 1)
        page_and_total = response.xpath("//span[contains(@class, 'pagination-btn count')]/text()").extract_first(None)
        try:
            page_nums, total_nums = self.get_two(page_and_total)
        except:
            page_nums, total_nums = 0, 0
        category_loader.add_value("publish_nums", total_nums)
        category_item = category_loader.load_item()
        yield category_item

        for page in self.parse_partial(range(1, page_nums + 1)):
            request_url = response.url + "#/all/default/0/{}/".format(page)
            yield scrapy.Request(url=request_url, callback=self.parse_page,
                                 dont_filter=True, meta={"url": request_url})
                                                         # "browser": response.meta['browser']})

    def parse_page(self, response):
        """解析分类页"""
        ele = pyquery.PyQuery(response.text)
        video_list = ele.find("a.title")
        if video_list:
            for video in video_list:
                url = None
                for k, v in video.items():
                    if k == "href":
                        url = urljoin(self.base_url, v)
                        break
                if url:
                    # 解析video
                    yield scrapy.Request(url=url, callback=self.parse_detail, dont_filter=True)

    def parse_detail(self, response):
        """解析Video"""
        detail_loader = DefaultItemLoader(VideoItem(), response=response)
        detail_loader.add_value("vid", get_id(response.url))
        detail_loader.add_xpath("author", "//div[contains(@class, 'user')]/a[contains(@class, 'name')]/text()")
        detail_loader.add_xpath("title", "//h1/@title")
        detail_loader.add_xpath("desc", "//div[@id='v_desc']/div[contains(@class, 'info')]")
        detail_loader.add_value("url", response.url)
        detail_loader.add_xpath('play_nums', "substring(//span[contains(@class, 'v play')]/@title, 5)")
        detail_loader.add_xpath('danmu_nums', "substring(//span[contains(@class, 'v dm')]/@title, 5)")
        detail_loader.add_xpath('coins', "substring(//span[@report-id='coinbtn1']/@title, 6)")
        detail_loader.add_xpath('collections', "substring(//span[@report-id='collect1']/@title, 5)")
        detail_loader.add_value('comments', response.meta.get('comments', 0))
        detail_loader.add_xpath('shares', "//div[@id='playpage_share']//span[@class='num']/text()")
        detail_loader.add_value('likes', response.meta.get("likes", 0))
        detail_loader.add_xpath("publish_time", "//time/text()")
        detail_loader.add_xpath("category", "//div[contains(@class, 'tminfo')]/span/a/text()")
        detail_loader.add_xpath("tags", "//ul[contains(@class, 'tag-area')]/li/a/text()")
        detail_item = detail_loader.load_item()
        self.crawler.stats.inc_value("detail_item")
        yield detail_item

        if PARSE_COMMENTS:
            for item in self.gen_comments_item(response):
                yield item
        # else:
        #     self.queue.put(response.meta.get("browser"))

    def parse_person(self, response):
        # self.queue.put(response.meta.get("browser"))
        person_item_loader = DefaultItemLoader(PersonItem(), response=response)
        person_item_loader.add_xpath("name", "//span[@id='h-name']/text()")
        person_item_loader.add_xpath("gender", "//span[@id='h-gender']/@class")
        person_item_loader.add_xpath("sign", "//*[@class='h-sign']/text()")
        person_item_loader.add_xpath("level", "//a[contains(@class, 'h-level')]/@lvl")
        person_item_loader.add_xpath("avatar", "//img[@id='h-avatar']/@src")
        person_item_loader.add_xpath("uid", "//div[contains(@class, 'uid')]/span[@class='text']/text()")
        person_item_loader.add_xpath("birthday", "//div[contains(@class, 'birthday')]/span[@class='text']/text()")
        person_item_loader.add_xpath("attention_nums", "//a[contains(@class, 'n-gz')]/@title")
        person_item_loader.add_xpath("fans_nums", "//a[contains(@class, 'n-fs')]/@title")
        person_item_loader.add_xpath("play_nums", "//div[contains(@class, 'n-bf')]/@title")
        person_item_loader.add_xpath("register_time", "//div[contains(@class, 'regtime')]/span[@class='text']/text()")
        person_item_loader.add_xpath("member_level", "//a[contains(@class, 'h-vipType')]/@class")
        person_item_loader.add_xpath("play_game_list", "//div[contains(@class, 'game')]//div[@class='detail']/text()")
        person_item_loader.add_xpath("tags", "//div[contains(@class, 'tag-list')]/a/text()")
        person_item = person_item_loader.load_item()
        yield person_item

    def parse_article(self, response):
        article_item_loader = DefaultItemLoader(ArticleItem(), response=response)
        article_item_loader.add_xpath("author", "//a[@class='up-name']/text()")
        article_item_loader.add_xpath("cover_img_url", "//div[@class='banner-img-holder']/@style")
        article_item_loader.add_xpath("title", "//h1[@class='title']/text()")
        article_item_loader.add_xpath("desc", "//div[contains(@class, 'article-holder')]/p/text()")
        article_item_loader.add_value("url", response.url)
        article_item_loader.add_value("cid", get_id(response.url))
        article_item_loader.add_xpath("img_box", "//figure[@class='img-box']/img/@data-src")
        article_item_loader.add_xpath("views", "//div[@class='article-data']/span[1]/text()")
        article_item_loader.add_xpath("likes", "//div[@class='article-data']/span[2]/text()")
        article_item_loader.add_xpath("comments", "//div[@class='article-data']/span[3]/text()")
        article_item_loader.add_xpath("coins", "//div[@class='coin-btn']/div/span/text()")
        article_item_loader.add_xpath("collections", "//div[@class='fav-btn']/div/span/text()")
        article_item_loader.add_xpath("shares", "//div[@class='share-btn']/div/span/text()")
        article_item_loader.add_xpath("publish_time", "//span[@class='create-time']/text()")
        article_item_loader.add_xpath("category", "//a[@class='category-link']/span/text()")
        article_item_loader.add_xpath("tags", "//li[@class='tag-item']/span[2]/text()")
        article_item = article_item_loader.load_item()
        yield article_item

        if PARSE_COMMENTS:
            for item in self.gen_comments_item(response):
                yield item
        # else:
        #     self.queue.put(response.meta.get("browser"))

    def parse_tags(self, response):
        """解析标签页"""
        # self.queue.put(response.meta.get("browser"))
        tag_item_loader = DefaultItemLoader(item=TagItem(), response=response)
        tag_item_loader.add_xpath("name", "//div[@class='top-text']/text()")
        tag_item_loader.add_xpath("likes", "//div[@class='concern-num']/text()")
        tag_item_loader.add_xpath("publish_nums", "//div[@class='pageInfo']/span[2]/text()")
        tag_item = tag_item_loader.load_item()
        yield tag_item

    def handle_spider_closed(self, spider, reason):
        """爬虫结束信号处理"""
        self.browser.quit()

    def gen_comments_item(self, response):
        """派生器"""
        yield from self._parse_comments(response)

    def _parse_comments(self, response):
        """产出器, 用于解析视频或文章底下的评论"""
        # 评论页数
        for num in range(1, response.meta.get("page_nums", 0) + 1):
            browser = response.meta.get("browser")
            # comments = self.browser.find_elements_by_xpath("//div[contains(@class, 'list-item reply-wrap')]")
            comments = browser.find_elements_by_xpath("//div[contains(@class, 'list-item reply-wrap')]")
            # 点开所有更多回复
            # more = self.browser.find_elements_by_xpath("//a[@class='btn-more']")
            more = browser.find_elements_by_xpath("//a[@class='btn-more']")
            for item in more:
                item.click()
            # 遍历每层楼
            cnt = 0
            for comment in comments:
                # 主楼用户
                user = comment.find_element_by_xpath("div/div[@class='user']/a")
                yield from self._gen_main_comments(response, comment, user)
                yield from self._gen_reply_comments(response, comment, user, cnt)
                cnt += 1
            # self.browser.implicitly_wait(3)
            # self.browser.execute_script(self.script.commentPaninate.format(num+1))
            browser.implicitly_wait(3)
            browser.execute_script(self.script.commentPaninate.format(num+1))
            time.sleep(3)

    def _gen_main_comments(self, response, comment, user):
        """
        产出主楼评论item
        :param response: Response object
        :param comment: selenium element
        :return: CommentItem
        """
        desc = comment.find_element_by_xpath("div/p[@class='text']")
        # 评论信息
        info = comment.find_element_by_xpath("div/div[@class='info']")
        floor = info.find_element_by_xpath("span[@class='floor']")
        try:
            plad = info.find_element_by_xpath("span[@class='plad']")
        except Exception:
            plad = None
        cur_time = info.find_element_by_xpath("span[@class='time']")
        like = info.find_element_by_xpath("span[@class='like']")
        # 主楼item
        comment_loader = DefaultItemLoader(item=CommentItem(), response=response)
        comment_loader.add_value("source", response.url)
        comment_loader.add_value("sid", get_source(response.url))
        comment_loader.add_value("person", user.text)
        comment_loader.add_value("desc", desc.text)
        comment_loader.add_value("likes", like.text)
        comment_loader.add_value("plat_from", plad.text if plad else "PC端")
        comment_loader.add_value("reply_person", "")
        comment_loader.add_value("floor", floor.text)
        comment_loader.add_value("is_main", True)
        comment_loader.add_value("publish_time", createDatetime(cur_time.text))
        comment_item = comment_loader.load_item()
        yield comment_item

    def _gen_reply_comments(self, response, comment, user, cnt):
        """
        回复评论产出
        :param response: Response object
        :param comment: selenium element
        :param cnt: count for pagination
        :return: CommentItem
        """
        browser = response.meta.get("browser")
        # 寻找回复楼层页数及节点
        try:
            reply_page_element = comment.find_element_by_xpath("div/div[@class='paging-box']/span[@class='result']")
            replys = comment.find_elements_by_xpath("div/div[@class='reply-box']/div[contains(@class , 'reply-item')]")
            reply_page_num = GetNumber()(reply_page_element.text)[0]
            find_next = True
        except:
            reply_page_num = 2
            replys = []
            find_next = False
        # 由于回复楼层没有floor数, 需自行添加变量计数
        floor = 1
        for page in range(2, reply_page_num + 1):
            for reply in replys:
                # 楼中楼item
                rl_item_loader = DefaultItemLoader(item=CommentItem(), response=response)
                rl_user = reply.find_element_by_xpath("div/div[@class='user']/a")
                rl_desc = reply.find_element_by_xpath("div/div[@class='user']/span[@class='text-con']")
                rl_info = reply.find_element_by_xpath("div/div[@class='info']")
                rl_plad = "未知"
                rl_cur_time = rl_info.find_element_by_xpath("span[@class='time']")
                rl_like = rl_info.find_element_by_xpath("span[@class='like']")
                rl_person, rl_desc.data = find_reply_person(rl_desc.text)
                rl_item_loader.add_value("source", response.url)
                rl_item_loader.add_value("sid", get_source(response.url))
                rl_item_loader.add_value("person", rl_user.text)
                rl_item_loader.add_value("desc", getattr(rl_desc, "data", rl_desc.text))
                rl_item_loader.add_value("likes", rl_like.text)
                rl_item_loader.add_value("plat_from", rl_plad)
                rl_item_loader.add_value("reply_person", rl_person if rl_person else user.text)
                rl_item_loader.add_value("floor", floor)
                rl_item_loader.add_value("is_main", False)
                rl_item_loader.add_value("publish_time", createDatetime(rl_cur_time.text))
                rl_item = rl_item_loader.load_item()
                floor += 1
                yield rl_item
            # 如果页数大于1
            if find_next:
                # self.browser.implicitly_wait(3)
                # self.browser.execute_script(self.script.replyPaginate.format(cnt))
                browser.implicitly_wait(3)
                browser.execute_script(self.script.replyPaginate.format(cnt))
                replys = comment.find_elements_by_xpath("div/div[@class='reply-box']/div[contains(@class , 'reply-item')]")
                time.sleep(2)
