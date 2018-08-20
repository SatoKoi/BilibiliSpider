from django.db import models

# Create your models here.
from django.db.models import Model


class Tag(Model):
    """ 标签
    name: 标签名
    likes: 标签关注数
    publish_nums: 划分到该标签的视频数
    """
    tag_id = models.IntegerField(verbose_name="标签id", help_text="标签id", primary_key=True)
    name = models.CharField(verbose_name="标签名", help_text="标签名", max_length=30, unique=True)
    cover_url = models.CharField(verbose_name="标签图标", help_text="标签图标", max_length=255, null=True)
    likes = models.IntegerField(verbose_name="标签关注数", help_text="标签关注数", default=0)
    content = models.CharField(verbose_name="描述", help_text="描述", max_length=255, null=True)
    publish_nums = models.IntegerField(verbose_name="视频数", help_text="视频数", default=0)
    publish_time = models.DateTimeField(verbose_name="发布时间", help_text="发布时间", null=True)

    class Meta:
        verbose_name_plural = verbose_name = "标签"

    def __str__(self):
        return self.name


class Category(Model):
    """ 分类
    name: 分类名
    category_type: 分类等级
    parent: 父级分类
    publish_nums: 该分类下的投稿数
    """
    CATEGORY_TYPE = (
        (1, "一级类目"),
        (2, "二级类目"),
        # (3, "三级类目"),
    )
    name = models.CharField(verbose_name="分类名", help_text="分类名", max_length=30, unique=True)
    code = models.CharField(verbose_name="分类code", help_text="分类code", max_length=20, null=True)
    category_type = models.CharField(choices=CATEGORY_TYPE, max_length=10, verbose_name="分类等级", help_text="分类等级")
    parent = models.ForeignKey("self", verbose_name="父级分类", null=True, blank=True, help_text="父级分类",
                               on_delete=models.CASCADE, related_name="sub_cat")
    publish_nums = models.IntegerField(verbose_name="投稿数", help_text="投稿数", default=0)

    class Meta:
        verbose_name_plural = verbose_name = "分类"

    def __str__(self):
        return self.name


class Person(Model):
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
    SEX_CHOICES = (
        (0, "保密"),
        (1, "男"),
        (2, "女"),
    )
    MEMBER_CHOICES = (
        (0, "普通用户"),
        (1, "大会员"),
        (2, "年费大会员"),
    )
    name = models.CharField(verbose_name="用户名", help_text="用户名", max_length=30)
    gender = models.CharField(choices=SEX_CHOICES, max_length=4, verbose_name="性别", help_text="性别",
                              default="保密")
    sign = models.CharField(verbose_name="个性签名", help_text="个性签名", default="", max_length=200)
    uid = models.IntegerField(verbose_name="用户uid", help_text="用户uid", primary_key=True)
    level = models.IntegerField(verbose_name="用户等级", help_text="用户等级", default=0)
    birthday = models.DateField(verbose_name="用户生日", help_text="生日", null=True)
    avatar = models.CharField(verbose_name="用户头像", help_text="用户头像", default="", max_length=255)
    attention_nums = models.IntegerField(verbose_name="关注数", help_text="关注数", default=0)
    fans_nums = models.IntegerField(verbose_name="粉丝数", help_text="粉丝数", default=0)
    play_nums = models.IntegerField(verbose_name="播放数", help_text="播放数", default=0)
    register_time = models.DateTimeField(verbose_name="注册日期", help_text="注册日期")
    # play_game_list = models.CharField(verbose_name="最近玩过的游戏", help_text="最近玩过的游戏", max_length=200)
    member_level = models.CharField(choices=MEMBER_CHOICES, verbose_name="会员等级", help_text="会员等级", max_length=6)
    # subscribe_tags = models.ManyToManyField(TagModel)
    tags = models.CharField(verbose_name="标签集", help_text="标签集", max_length=200)

    class Meta:
        verbose_name_plural = verbose_name = "用户"

    def __str__(self):
        return self.name


class Video(Model):
    """ 视频
    author: up主
    title: 标题
    desc: 描述
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
    # author = models.ForeignKey(PersonModel, on_delete=models.CASCADE, verbose_name="up主", help_text="up主")
    vid = models.IntegerField(verbose_name="av号", help_text="av号", primary_key=True)
    author = models.CharField(verbose_name="up主", help_text="up主", max_length=30)
    title = models.CharField(verbose_name="标题", help_text="标题", max_length=50)
    desc = models.TextField(verbose_name="描述", help_text="描述")
    url = models.CharField(verbose_name="链接地址", help_text="链接", max_length=255)
    play_nums = models.IntegerField(verbose_name="播放数", help_text="播放数", default=0)
    danmu_nums = models.IntegerField(verbose_name="弹幕数", help_text="弹幕数", default=0)
    comments = models.IntegerField(verbose_name="评论数", help_text="评论数", default=0)
    coins = models.IntegerField(verbose_name="硬币数", help_text="硬币数", default=0)
    collections = models.IntegerField(verbose_name="收藏数", help_text="收藏数", default=0)
    likes = models.IntegerField(verbose_name="点赞数", help_text="点赞数", default=0)
    shares = models.IntegerField(verbose_name="分享数", help_text="分享数", default=0)
    publish_time = models.DateTimeField(verbose_name="发布日期", help_text="发布日期")
    tags = models.CharField(verbose_name="标签集", help_text="标签集", max_length=200, null=True)
    category = models.CharField(verbose_name="分类集", help_text="分类集", max_length=50)
    # category = models.ForeignKey(CategoryModel, on_delete=models.CASCADE)
    # tags = models.ManyToManyField(TagModel)

    class Meta:
        verbose_name_plural = verbose_name = "视频"

    def __str__(self):
        return "[{}]:[{}]".format(self.author, self.title)


class Article(Model):
    cid = models.IntegerField(verbose_name="cv号", help_text="cv号", primary_key=True)
    author = models.CharField(verbose_name="up主", help_text="up主", max_length=30)
    title = models.CharField(verbose_name="标题", help_text="标题", max_length=50)
    desc = models.TextField(verbose_name="描述", help_text="描述")
    url = models.CharField(verbose_name="链接地址", help_text="链接", max_length=255)
    cover_img_url = models.CharField(verbose_name="封面图", help_text="封面图", max_length=255, null=True)
    img_box = models.TextField(verbose_name="图源箱", help_text="图源箱", null=True)
    views = models.IntegerField(verbose_name="阅读数", help_text="阅读数", default=0)
    comments = models.IntegerField(verbose_name="评论数", help_text="评论数", default=0)
    coins = models.IntegerField(verbose_name="硬币数", help_text="硬币数", default=0)
    collections = models.IntegerField(verbose_name="收藏数", help_text="收藏数", default=0)
    likes = models.IntegerField(verbose_name="喜欢数", help_text="喜欢数", default=0)
    shares = models.IntegerField(verbose_name="分享数", help_text="分享数", default=0)
    publish_time = models.DateTimeField(verbose_name="发布日期", help_text="发布日期")
    tags = models.CharField(verbose_name="标签集", help_text="标签集", max_length=200, null=True)
    category = models.CharField(verbose_name="分类集", help_text="分类集", max_length=50)

    class Meta:
        verbose_name_plural = verbose_name = "文章"

    def __str__(self):
        return "[{}]:[{}]".format(self.author, self.title)


class Comment(Model):
    """ 评论
    source: 来源
    person: 评论用户
    desc: 评论描述
    likes: 点赞数
    plat_from: 平台
    reply_person: 被回复人
    """
    Choices = (
        (0, '未知'),
        (1, "PC端"),
        (2, "安卓客户端"),
        (3, "IOS客户端"),
        (4, "其他")
    )
    sid = models.CharField(verbose_name="id号", help_text="id号", null=True, max_length=30)
    source = models.CharField(verbose_name="来源url", help_text="来源url", max_length=255)
    # person = models.ForeignKey(PersonModel, on_delete=models.CASCADE, verbose_name="评论用户", related_name="person")
    person = models.CharField(verbose_name="评论用户", help_text="评论用户", max_length=30)
    desc = models.TextField(verbose_name="内容", help_text="内容")
    likes = models.IntegerField(verbose_name="点赞数", help_text="点赞数", default=0)
    plat_from = models.CharField(verbose_name="平台", help_text="平台", default="PC端", max_length=30)
    # reply_person = models.ForeignKey(PersonModel, on_delete=models.CASCADE, verbose_name="被回复用户", related_name="reply_person")
    reply_person = models.CharField(verbose_name="被回复用户", help_text="被回复用户", max_length=30, null=True)
    floor = models.IntegerField(verbose_name='楼层', help_text="楼层", default=0)
    is_main = models.BooleanField(verbose_name="是否主楼", help_text="是否主楼", default=True)
    publish_time = models.DateTimeField(verbose_name="发布时间", help_text="发布时间", null=True)
    type = models.CharField(verbose_name="种类", help_text="种类", choices=((0, "视频"), (1, "文章")), default=0, max_length=4)

    class Meta:
        verbose_name_plural = verbose_name = "评论"
        unique_together = ('sid', 'person', 'floor', 'publish_time')

    def __str__(self):
        return self.person