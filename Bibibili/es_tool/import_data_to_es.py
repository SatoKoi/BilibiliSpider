# -*- coding:utf-8 -*-
import pickle
import os
import sys
import django
import atexit
from es_tool.models import ArticleDocType, VideoDocType
from elasticsearch_dsl.connections import connections

pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd + "../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Bibibili.settings")
django.setup()

from Bili.models import Article, Video, Comment, Tag, Person

es = connections.create_connection(ArticleDocType._doc_type.using)


def load_batch_size(filepath):
    """从文件中读取batch_size"""
    if not os.path.exists(pickle_file_dir):
        os.mkdir(pickle_file_dir)
    if os.path.isfile(filepath):
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        return data.get('batch_size')
    else:
        with open(filepath, 'wb') as f:
            pickle.dump({"batch_size": 0}, f)
        return 0


def save_batch_size(fobj, batch_size):
    """保存batch数据"""
    pickle.dump({"batch_size": batch_size}, fobj)


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
            try:
                words = es.indices.analyze(index=index, params={'analyzer': 'ik_max_word', 'filter': ["lowercase"]}, body=text)
            except:
                raise Exception("The words can't be analyzed")
            # 从token中得到所有由analyzer分析得到的分词
            analyzed_words = set([r["token"] for r in words["tokens"] if len(r['token']) > 1])
            # 得到所有未使用的分词
            new_words = analyzed_words - used_words  # 差集
        else:
            new_words = set()

        if new_words:
            suggests.append({"input": list(new_words), "weight": weight})
    return suggests


class Model(object):
    method_object = {
        "article": Article,
        "video": Video,
        "comment": Comment,
        "tag": Tag,
        "person": Person,
    }

    def _load_data(self, pickle_file_path: str, method_str: str):
        """载入数据 batch_size, total_count, model"""
        batch_size = load_batch_size(pickle_file_path)
        print("上次导入batch位置: {}".format(batch_size))
        obj = self.method_object.get(method_str, None)
        if obj:
            total_count = obj.objects.all().count()
            print("总共数据量: {}".format(total_count))
            setattr(self, '{}_total_count'.format(method_str), total_count)
            return batch_size, total_count, obj
        else:
            raise Exception("Can't resolve method_str to method")

    def get_truncate_end(self, batch_size, total_count):
        """获取输入数据"""
        try:
            truncate_end = int(input("批处理截止位置: "))
            if truncate_end > total_count or truncate_end <= batch_size:
                raise ValueError
            return truncate_end
        except ValueError:
            print("请输入合适的批处理位置")
            sys.exit(1)

    def save_model(self, methods, pickle_file_path):
        """通用方法"""
        batch_size, total_count, model = self._load_data(pickle_file_path, methods)
        truncate_end = self.get_truncate_end(batch_size, total_count)

        # 注册 结束时关闭文件
        fobj = open(pickle_file_path, 'wb')
        atexit.register(lambda fobj: fobj.close(), fobj=fobj)

        # 循环导入数据
        while True:
            print("开始导入第{}个数据".format(batch_size))
            objs = model.objects.all()[batch_size: batch_size + step]
            for obj in objs:
                self._save_model(obj, methods)
            batch_size += step
            if not batch_size < truncate_end:
                save_batch_size(fobj, truncate_end)
                print("停止导入")
                break
        setattr(self, "{}_batch_size".format(methods), truncate_end)

    def _save_model(self, obj, methods):
        if methods == "article":
            self._save_article(obj)
        elif methods == "video":
            self._save_video(obj)

    @classmethod
    def save_article_to_es(cls, pickle_file_path):
        """批保存文章至es中"""
        self = cls()
        self.save_model("article", pickle_file_path)
        return self

    @classmethod
    def save_video_to_es(cls, pickle_file_path):
        self = cls()
        self.save_model("video", pickle_file_path)
        return self

    def _save_article(self, article):
        """保存文章数据到es中"""
        article_doc = ArticleDocType()
        article_doc.cid = article.cid
        article_doc.author = article.author
        article_doc.cover_img_url = article.cover_img_url
        article_doc.title = article.title
        article_doc.desc = article.desc
        article_doc.url = article.url
        article_doc.views = article.views
        article_doc.comments = article.comments
        article_doc.coins = article.coins
        article_doc.collections = article.collections
        article_doc.likes = article.likes
        article_doc.shares = article.shares
        article_doc.publish_time = article.publish_time
        article_doc.category = article.category
        article_doc.tags = article.tags
        try:
            article_doc.suggest = gen_suggests(article_doc._doc_type.index, ((article.title, 10),
                                                                             (article.desc, 8),
                                                                             (article.category, 6),
                                                                             (article.tags, 4),
                                                                             (article.author, 3)))
        except Exception:
            pass
        article_doc.save()

    def _save_video(self, video):
        video_doc = VideoDocType()
        video_doc.vid = video.vid
        video_doc.author = video.author
        video_doc.title = video.title
        video_doc.desc = video.desc
        video_doc.url = video.url
        video_doc.play_nums = video.play_nums
        video_doc.danmu_nums = video.danmu_nums
        video_doc.comments = video.comments
        video_doc.coins = video.coins
        video_doc.collections = video.collections
        video_doc.likes = video.likes
        video_doc.shares = video.shares
        video_doc.publish_time = video.publish_time
        video_doc.category = video.category
        video_doc.tags = video.tags
        try:
            video_doc.suggest = gen_suggests(video._doc_type.index, ((video.title, 10),
                                                                     (video.desc, 8),
                                                                     (video.category, 6),
                                                                     (video.tags, 4),
                                                                     (video.author, 3)))
        except Exception:
            pass
        video_doc.save()

    def get_size(self, method):
        size = getattr(self, "{}_batch_size".format(method), None)
        if not size:
            raise Exception("Be able to get article_size must behind using save_article_to_es method")
        return size

    @property
    def article_size(self):
        return self.get_size("article")

    @property
    def video_size(self):
        return self.get_size("video_size")


if __name__ == '__main__':
    pickle_file_dir = os.path.join(os.path.dirname(os.path.abspath(__name__)), 'pickle')
    pickle_file_path = os.path.join(pickle_file_dir, 'article.pickle')
    step = 20
    model = Model.save_article_to_es(pickle_file_path)
    print(model.article_size)
