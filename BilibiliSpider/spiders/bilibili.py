# -*- coding:utf-8 -*-
import json
import os
import scrapy

from scrapy import signals
from pydispatch import dispatcher
from scrapy_redis.spiders import RedisSpider
from selenium.webdriver import ChromeOptions
# from requests.utils import cookiejar_from_dict

from ..mixins import *
from ..items import *
from ..map.defaults import *
from ..settings import *
from ..utils.metrics import *


class BilibiliSpider(GetCookieMixin, ReplyMixin, RedisSpider):
    name = 'bilibili'
    allowed_domains = ['www.bilibili.com', 'space.bilibili.com', 'api.bilibili.com', 'bangumi.bilibili.com']
    base_url = "https://www.bilibili.com/"
    redis_key = "bilibili:urls"

    custom_settings = {
        'COOKIES_ENABLED': True,
        'DOWNLOADER_DELAY': 1,
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

    chrome_options = ChromeOptions()

    api_urls = {
        # 'archive': 'http://api.bilibili.com/archive_rank/getarchiverankbypartion?tid={tid}&pn={pn}',     # 分类接口1
        'archive': 'https://api.bilibili.com/x/web-interface/newlist?rid={tid}&type=0&pn={pn}&ps=30',      # 分类接口2
        'videostats': 'https://api.bilibili.com/x/web-interface/archive/stat?aid={id}',                    # video数据
        'vcomments': 'https://api.bilibili.com/x/v2/reply?pn={pn}&type=1&oid={id}&ps=20',                  # video下的评论
        'vreply': 'https://api.bilibili.com/x/v2/reply/reply?pn={pn}&type=1&oid={id}&root={root}&ps=20',   # video评论中的回复
        'vtags': 'https://api.bilibili.com/x/tag/archive/tags?aid={id}',                                   # video下的标签
        'acomments': 'https://api.bilibili.com/x/v2/reply?&pn={pn}&type=12&oid={id}',                      # article下的评论
        'areply': 'https://api.bilibili.com/x/v2/reply/reply?&pn={pn}&type=12&oid={id}&root={root}',       # article评论中的回复
        'articlestats': 'https://api.bilibili.com/x/article/viewinfo?id={id}',                             # article中的数据
        'userstats': 'https://space.bilibili.com/ajax/member/GetInfo',                                     # user数据 post方法 mid, csrf
        'fstats': 'https://api.bilibili.com/x/relation/stat?vmid={id}',                                    # user粉丝及关注
        'upstats': 'https://api.bilibili.com/x/space/upstat?mid={id}',                                     # user播放量
        'tagstats': 'https://space.bilibili.com/ajax/tags/getSubList?mid={id}',                            # user标签
        'uservideostats': 'https://space.bilibili.com/ajax/member/getSubmitVideos?mid={id}&page={pn}',     # user发布的新视频
        'tstats': 'https://api.bilibili.com/x/tag/info?tag_id={id}',                                       # tag数据
        'online': 'https://api.bilibili.com/x/web-interface/online',                                       # online人数
        'blackroom': 'https://api.bilibili.com/x/v2/reply?pn=2&type=6&oid={id}',                           # 小黑屋
        'postreply': 'https://api.bilibili.com/x/v2/reply/add',                                            # 发表评论
        'dynamic': 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/dynamic_new?uid={id}&type=8'    # 获取动态
    }

    def __init__(self, *args, **kwargs):
        # self.browser = Chrome(executable_path="F:\ChromeDriver\chromedriver.exe", chrome_options=self.chrome_options)
        # browser.find_element_by_xpath("//input[@id='login-username']").send_keys("")
        # browser.find_element_by_xpath("//input[@id='login-passwd']").send_keys("")
        self.mapping = {}
        with open('BilibiliSpider/map/tag.json', 'r', encoding='utf8') as f:
            self.mapping = json.load(f)
        self.reg_pattern = REG_PATTERN
        self.partial = iter if PARSE_DETAIL_ORDER_ASC else reversed
        self.cookies = self.get_cookies()
        self.csrf = self.cookies.get('bili_jct', "")  # 填写登录后的cookie bili_jct, 用作post时的csrf字段
        dispatcher.connect(self.handle_spider_closed, signals.spider_closed)
        super(BilibiliSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        """选择一个解析函数"""
        parse_res = urlparse(response.url)
        result = re.match(self.reg_pattern['video'], parse_res.path, re.I)
        if result:
            response.meta['video_id'] = result.group(1)
            return self.parse_detail(response)

        if parse_res.netloc == self.allowed_domains[1]:
            result = re.match(self.reg_pattern['user'], parse_res.path, re.I)
            if result:
                response.meta['user_id'] = result.group(1)
                return self.parse_person(response)

        result = re.match(self.reg_pattern['article'], parse_res.path, re.I)
        if result:
            response.meta['article_id'] = result.group(1)
            return self.parse_article(response)

        result = re.match(self.reg_pattern['tag'], parse_res.path, re.I)
        if result:
            response.meta['tag_id'] = result.group(1)
            return self.parse_tags(response)

        if re.match(self.reg_pattern['online'], parse_res.path, re.I) \
                and parse_res.netloc == self.allowed_domains[2]:
            return self.parse_online(response)

        if re.match(self.reg_pattern['reply'], parse_res.path):
            return self.reply(response)
        return []

    def parse_detail(self, response):
        """只针对video数据和相关评论进行抓取"""
        video_url = self.api_urls.get('videostats')
        comment_url = self.api_urls.get('vcomments')
        video_id = response.meta.get('video_id')
        detail_loader = DefaultItemLoader(VideoItem(), response=response)
        detail_loader.add_value("vid", video_id)
        detail_loader.add_value("url", response.url)
        detail_loader.add_xpath("author", "//div[contains(@class, 'user')]/a[contains(@class, 'name')]/text()")
        detail_loader.add_xpath("title", "//h1/@title")
        detail_loader.add_xpath("desc", "//div[@id='v_desc']/div[contains(@class, 'info')]")
        detail_loader.add_xpath("publish_time", "//time/text()")
        detail_loader.add_xpath("category", "//div[contains(@class, 'tminfo')]/span/a/text()")
        detail_loader.add_xpath("tags", "//ul[contains(@class, 'tag-area')]/li/a/text()")
        detail_item = detail_loader.load_item()
        yield scrapy.Request(url=video_url.format(id=video_id),
                             dont_filter=True,
                             callback=self._parse_detail_stats,
                             meta={'item': detail_item}
                             )
        if PARSE_COMMENTS:
            # 评论入口页不去重
            yield scrapy.Request(url=comment_url.format(pn=1, id=video_id),
                                 callback=self.parse_comment,
                                 dont_filter=True,
                                 meta={'source': response.url,
                                       'sid': video_id,
                                       'url': comment_url,
                                       'reply_url': self.api_urls.get('vreply')}
                                 )

    def _parse_detail_stats(self, response):
        """解析需要异步获取的数据"""
        decode_data = self.decode_data(response.text)
        item = response.meta.get('item')
        item['play_nums'] = decode_data.get('view', 0)
        item['danmu_nums'] = decode_data.get('danmaku', 0)
        item['comments'] = decode_data.get('reply', 0)
        item['collections'] = decode_data.get('favorite', 0)
        item['coins'] = decode_data.get('coin', 0)
        item['shares'] = decode_data.get('share', 0)
        item['likes'] = decode_data.get('like', 0)
        yield item

    def parse_article(self, response):
        """只针对article数据和相关评论进行抓取"""
        article_id = response.meta.get('article_id')
        article_item_loader = DefaultItemLoader(ArticleItem(), response=response)
        article_item_loader.add_value("url", response.url)
        article_item_loader.add_value("cid", article_id)
        article_item_loader.add_xpath("desc", "//div[contains(@class, 'article-holder')]/p/text()")
        article_item_loader.add_xpath("publish_time", "//span[@class='create-time']/@data-ts")
        article_item_loader.add_xpath("category", "//a[@class='category-link']/span/text()")
        article_item_loader.add_xpath("tags", "//li[@class='tag-item']/span[2]/text()")
        article_item = article_item_loader.load_item()
        yield scrapy.Request(url=self.api_urls.get('articlestats').format(id=article_id),
                             dont_filter=True,
                             callback=self._parse_article_stats,
                             meta={'item': article_item}
                             )
        if PARSE_COMMENTS:
            yield scrapy.Request(url=self.api_urls.get('acomments').format(id=article_id, pn=1),
                                 dont_filter=True,
                                 callback=self.parse_comment,
                                 meta={"url": self.api_urls.get('acomments'),
                                       'sid': article_id,
                                       'source': response.url,
                                       'reply_url': self.api_urls.get("areply")}
                                 )

    def _parse_article_stats(self, response):
        """抓取文章数据"""
        decode_data = self.decode_data(response.text)
        stats = decode_data['stats']
        item = response.meta.get('item')
        item['cover_img_url'] = decode_data.get('banner_url', "")
        item['img_box'] = decode_data.get('image_urls', [])
        item['author'] = decode_data.get('author_name', "")
        item['title'] = decode_data.get('title', "")
        item['views'] = stats.get('view', 0)
        item['comments'] = stats.get('reply', 0)
        item['coins'] = stats.get('coin', 0)
        item['collections'] = stats.get('favorite', 0)
        item['likes'] = stats.get('like', 0)
        item['shares'] = stats.get('share', 0)
        yield item

    def parse_comment(self, response):
        """爬取相应的评论"""
        decode_data = self.decode_data(response.text)
        page = decode_data['page']
        acount = page.get('account', 0)
        count = page.get('count', 0)
        max_pn = count // page.get('size', 20) + 1
        if max_pn > PARSE_COMMENTS_MAX_PAGES:
            max_pn = PARSE_COMMENTS_MAX_PAGES
        url = response.meta.get('url')
        for pn in self.partial(range(1, max_pn+1)):
            yield scrapy.Request(url=url.format(pn=pn, id=response.meta.get('sid')),
                                 callback=self.parse_comment_page,
                                 meta=response.meta
                                 )

    def parse_comment_page(self, response):
        """单页comment parse"""
        decode_data = self.decode_data(response.text)
        replies = decode_data.get('replies')
        sid, source = response.meta.get('sid'), response.meta.get('source')
        for reply in replies:
            yield from self._gen_reply(reply, sid, source)
            # 如果设置了PARSE_CHILD_COMMENTS为True, 且该评论能找到回复内容不为空
            if PARSE_CHILD_COMMENTS and reply.get('replies'):
                root = reply.get("rpid")
                # 回复入口页不去重
                reply_url = response.meta['reply_url']
                yield scrapy.Request(url=reply_url.format(pn=1, root=root, id=sid),
                                     dont_filter=True,
                                     callback=self.parse_reply,
                                     meta={'root': root,
                                           'sid': sid,
                                           'source': response.meta.get('source'),
                                           'reply_url': reply_url}
                                     )

    def parse_reply(self, response):
        """抓取评论中回复"""
        decode_data = self.decode_data(response.text)
        count = decode_data['page'].get('count', 0)
        max_pn = count // decode_data['page'].get('size', 50) + 1
        if max_pn > PARSE_CHILD_COMMENTS_MAX_PAGES:
            max_pn = PARSE_CHILD_COMMENTS_MAX_PAGES
        sid, source = response.meta.get('sid'), response.meta.get('source')
        reply_url = response.meta['reply_url']
        for pn in self.partial(range(1, max_pn + 1)):
            yield scrapy.Request(url=reply_url.format(pn=pn, id=response.meta.get('sid'), root=response.meta.get('root')),
                                 callback=self.parse_reply_page,
                                 meta={'sid': sid,
                                       'source': source}
                                 )

    def parse_reply_page(self, response):
        """单页reply parse"""
        decode_data = self.decode_data(response.text)
        replies = decode_data.get('replies')
        sid, source = response.meta.get('sid'), response.meta.get('source')
        reply_person = decode_data.get('root')['member'].get('uname')
        for reply in replies:
            yield from self._gen_reply(reply, sid, source, is_main=False, reply_p=reply_person)

    def _gen_reply(self, reply, sid, source, is_main=True, reply_p=None):
        """reply产出"""
        comment_loader = DefaultItemLoader(CommentItem())
        comment_loader.add_value('sid', sid)
        comment_loader.add_value('source', source)
        comment_loader.add_value('person', reply['member']['uname'])
        message = reply['content']['message']
        reply_person, message = find_reply_person(message)
        if not is_main and not reply_person:
            reply_person = reply_p
        comment_loader.add_value('desc', message)
        comment_loader.add_value('likes', reply['like'])
        comment_loader.add_value('plat_from', get_plat(reply['content'].get('plat', 0)))
        comment_loader.add_value('reply_person', reply_person if reply_person else "")
        comment_loader.add_value('floor', reply['floor'])
        comment_loader.add_value('is_main', is_main)
        comment_loader.add_value('publish_time', datetime.fromtimestamp(reply['ctime']))
        comment_loader.add_value('type', get_type(source))
        item = comment_loader.load_item()
        yield item

    def parse_person(self, response):
        """只针对user数据进行抓取"""
        user_id = response.meta.get('user_id')
        form_data = {
            'mid': user_id,
            'csrf': self.csrf
        }
        # 此处需要post方能拿到数据
        yield scrapy.FormRequest(url=self.api_urls.get("userstats").format(id=user_id),
                                 formdata=form_data,
                                 dont_filter=True,
                                 callback=self._parse_person_stats,
                                 meta={'user_id': user_id,
                                       'url': response.url}
                                 )

    def _parse_person_stats(self, response):
        """user基本信息"""
        decode_data = self.decode_data(response.text)
        if decode_data['status']:
            person_loader = DefaultItemLoader(PersonItem(), response=response)
            person_loader.add_value('name', decode_data.get('name'))
            person_loader.add_value('gender', decode_data.get('gender'))
            person_loader.add_value('sign', decode_data.get('sign'))
            person_loader.add_value('uid', decode_data.get('mid'))
            person_loader.add_value('level', decode_data['level_info'].get('current_level', 0))
            person_loader.add_value('birthday', decode_data.get('birthday'))
            person_loader.add_value('avatar', decode_data.get('face'))
            person_loader.add_value('member_level', decode_data['vip'].get('vipType', 0))
            person_loader.add_value('register_time', decode_data.get('regtime'))
            person_item = person_loader.load_item()
            yield scrapy.Request(url=self.api_urls.get('fstats').format(id=response.meta.get('user_id')),
                                 callback=self._parse_person_fstats,
                                 dont_filter=True,
                                 meta={'person_item': person_item,
                                       'user_id': response.meta.get('user_id')}
                                 )
        else:
            yield scrapy.Request(url=response.meta['url'], meta={'status': 404, 'key': 'user' + response.meta.get('user_id')})

    def _parse_person_fstats(self, response):
        """user粉丝关注信息"""
        decode_data = self.decode_data(response.text)
        person_item, user_id = response.meta['person_item'], response.meta['user_id']
        person_item['attention_nums'] = decode_data['following']
        person_item['fans_nums'] = decode_data['follower']
        yield scrapy.Request(url=self.api_urls.get('upstats').format(id=user_id),
                             dont_filter=True,
                             callback=self._parse_person_upstats,
                             meta=response.meta
                             )

    def _parse_person_upstats(self, response):
        """user播放量信息"""
        decode_data = self.decode_data(response.text)
        person_item = response.meta['person_item']
        person_item['play_nums'] = decode_data['archive'].get('view', 0)
        yield scrapy.Request(url=self.api_urls.get('tagstats').format(id=response.meta['user_id']),
                             dont_filter=True,
                             callback=self._parse_person_tagstats,
                             meta=response.meta
                             )

    def _parse_person_tagstats(self, response):
        """user关注tag标签信息"""
        decode_data = self.decode_data(response.text)
        person_item = response.meta['person_item']
        person_item['tags'] = ','.join([tag.get('name', "") for tag in decode_data.get('tags', {})])
        yield person_item

    def parse_tags(self, response):
        """只针对tag数据进行抓取"""
        tag_loader = DefaultItemLoader(TagItem(), response=response)
        tag_loader.add_value('tag_id', response.meta['tag_id'])
        tag_loader.add_xpath('publish_nums', '//div[@class="pageInfo"]/span[2]/text()')
        tag_item = tag_loader.load_item()
        yield scrapy.Request(url=self.api_urls.get('tstats').format(id=response.meta['tag_id']),
                             dont_filter=True,
                             callback=self._parse_tags_stats,
                             meta={'tag_item': tag_item,
                                   'url': response.url,
                                   'tag_id': response.meta['tag_id']})

    def _parse_tags_stats(self, response):
        decode_data = self.decode_data(response.text)
        if decode_data:
            tag_item = response.meta['tag_item']
            tag_item['name'] = decode_data['tag_name']
            tag_item['likes'] = decode_data['count'].get('atten', 0)
            tag_item['content'] = decode_data['content']
            tag_item['cover_url'] = decode_data['cover']
            tag_item['publish_time'] = decode_data['ctime']
            yield tag_item
        else:
            yield scrapy.Request(url=response.meta['url'], meta={'status': 404, 'key': 'tag' + response.meta.get('tag_id')})

    def parse_online(self, response):
        """针对b站在线人数进行抓取"""
        yield from self._gen_online(response)

    def _gen_online(self, response):
        """online产出"""
        decode_data = self.decode_data(response.text)
        item = OnlineItem()
        item['all_count'] = decode_data.get('all_count', 0)
        item['web_online'] = decode_data.get('web_online', 0)
        item['play_online'] = decode_data.get('play_online', 0)
        item['current_time'] = datetime.now()
        yield item

    def check_status(self, response):
        """检查post回复的状态"""
        root_data = json.loads(response.text)
        if root_data['code'] == 0 and len(root_data['data']):
            dispatcher.connect(self.handle_success, signals=signals.response_received)
        else:
            dispatcher.connect(self.handle_exception, signals=signals.spider_error)

    def decode_data(self, text):
        """返回decode json类型的python对象"""
        try:
            data = json.loads(text)
            status = data.get('status', True)
            code = data.get('code', 0)
            data = data['data']
            if isinstance(data, dict):
                data.update({'status': status, "code": code})
            if isinstance(data, str):
                data = {"msg": data, 'status': status, "code": code}
            return data
        except:
            dispatcher.connect(self.handle_nodata, signals.request_dropped)
            return {}

    def handle_success(self, spider, reason):
        spider.logger.info("Operation succeed!")

    def handle_nodata(self, spider, reason):
        spider.logger.error(reason)
        spider.logger.info("No data has been cralwed, the request url must have an invalid id")

    def handle_exception(self, spider, reason):
        spider.logger.error(reason)

    def handle_spider_closed(self, spider, reason):
        """爬虫结束信号处理"""
        spider.logger.info(self.crawler.stats)

