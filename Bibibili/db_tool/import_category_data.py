# -*- coding:utf-8 -*-
import sys
import os
import django

from db_tool.data.category_data import row_data

pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd + "../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Bibibili.settings")  # 设置环境变量

django.setup()

from Bili.models import Category

for category in row_data:
    category_instance = Category()
    category_instance.name = category['name']
    category_instance.code = category['code']
    category_instance.category_type = category['category_type']
    category_instance.parent = category['parent']
    category_instance.publish_nums = category['publish_nums']
    category_instance.save()