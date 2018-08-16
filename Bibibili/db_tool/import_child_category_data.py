# -*- coding:utf-8 -*-
import json
f1 = open('./data/data.json', 'r', encoding='utf8')
f2 = open('./data/data1.json', 'r', encoding='utf8')
row_data = json.load(f1)
row_data.extend(json.load(f2))

import sys
import os
import django

pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd + "../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Bibibili.settings")  # 设置环境变量

django.setup()

from Bili.models import Category
for category in row_data:
    category_instance, status = Category.objects.get_or_create(name=category['name'])
    category_instance.name = category['name']
    category_instance.code = category['code']
    category_instance.category_type = category['category_type']
    if not category_instance.parent:
        category_instance.parent = category['parent']
    category_instance.publish_nums = category['publish_nums']
    category_instance.save()