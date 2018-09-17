from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import *
from .serializers import *


class BasePagination(PageNumberPagination):
    page_size = 20                          # 默认分页大小
    page_size_query_param = "ps"            # 分页大小参数
    page_query_param = "pn"                 # 分页参数
    max_page_size = 30                      # 最大分页大小


class PersonViewset(ListModelMixin, GenericViewSet):
    throttle_classes = (UserRateThrottle, AnonRateThrottle)
    queryset = Person.objects.all().order_by('uid')
    serializer_class = PersonSerializer
    pagination_class = BasePagination
    search_fields = ('name', 'gender', 'level', 'member_level', 'sign')
    ordering_fields = ('uid', 'register_time', 'level', 'member_level', 'fans_nums', 'attention_nums',
                       'play_nums', 'coins', 'likes', 'collections')

    # 设置三大过滤器, 字段精确搜索, 广泛匹配过滤, 可排序过滤
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('name', 'uid', 'level', 'member_level')


class VideoViewset(ListModelMixin, GenericViewSet):
    throttle_classes = (UserRateThrottle, AnonRateThrottle)
    queryset = Video.objects.all().order_by('vid')
    serializer_class = VideoSerializer
    pagination_class = BasePagination
    search_fields = ('author', 'title', 'tags', 'category', 'desc')
    ordering_fields = ('vid', 'register_time', 'danmu_nums', 'comments',
                       'play_nums', 'coins', 'likes', 'collections', 'shares')

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('author', 'vid', 'title', 'desc')


class ArticleViewset(ListModelMixin, GenericViewSet):
    throttle_classes = (UserRateThrottle, AnonRateThrottle)
    queryset = Article.objects.all().order_by('cid')
    serializer_class = ArticleSerializer
    pagination_class = BasePagination
    search_fields = ('author', 'title', 'tags', 'category', 'desc')
    ordering_fields = ('cid', 'register_time', 'danmu_nums', 'comments',
                       'play_nums', 'coins', 'likes', 'collections', 'shares')

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('author', 'cid', 'title', 'desc')


class CommentViewset(ListModelMixin, GenericViewSet):
    throttle_classes = (UserRateThrottle, AnonRateThrottle)
    queryset = Comment.objects.all().order_by('id')
    serializer_class = CommentSerializer
    pagination_class = BasePagination
    search_fields = ('id', 'sid', 'person', 'desc', 'reply_person')
    ordering_fields = ('id', 'sid', 'likes', 'floor', 'is_main', 'publish_time')

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('id', 'sid', 'person', 'desc', 'reply_person')


class CategoryViewset(ListModelMixin, GenericViewSet):
    throttle_classes = (UserRateThrottle, AnonRateThrottle)
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    pagination_class = BasePagination
    search_fields = ('name', 'code')
    ordering_fields = ('id', 'publish_nums')

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('name', 'code', 'category_type', 'parent')


class TagViewset(ListModelMixin, GenericViewSet):
    throttle_classes = (UserRateThrottle, AnonRateThrottle)
    queryset = Tag.objects.all().order_by('id')
    serializer_class = CategorySerializer
    pagination_class = BasePagination
    search_fields = ('name', 'content')
    ordering_fields = ('tag_id', 'likes', 'publish_nums', 'publish_time')

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('name', 'content')