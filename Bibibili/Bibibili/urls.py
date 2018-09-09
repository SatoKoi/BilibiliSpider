"""Bibibili URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter

from Bili.views import *

import xadmin


router = DefaultRouter()
router.register(r'user', PersonViewset, base_name="user")
router.register(r'video', VideoViewset, base_name="video")
router.register(r'article', ArticleViewset, base_name="article")
router.register(r'category', CategoryViewset, base_name="category")
router.register(r'tags', TagViewset, base_name="tags")

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('xadmin/', xadmin.site.urls),
    path(r'docs/', include_docs_urls(title="B站爬虫数据接口")),
    path(r'', include(router.urls))
]
