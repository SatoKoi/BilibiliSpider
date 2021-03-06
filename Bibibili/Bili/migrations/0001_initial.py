# Generated by Django 2.0.3 on 2018-08-10 20:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='分类名', max_length=30, verbose_name='分类名')),
                ('category_type', models.CharField(choices=[(1, '一级类目'), (2, '二级类目'), (3, '三级类目')], help_text='分类等级', max_length=10, verbose_name='分类等级')),
                ('publish_nums', models.IntegerField(default=0, help_text='投稿数', verbose_name='投稿数')),
                ('parent', models.ForeignKey(blank=True, help_text='父级分类', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sub_cat', to='Bili.Category', verbose_name='父级分类')),
            ],
            options={
                'verbose_name': '分类',
                'verbose_name_plural': '分类',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(help_text='来源url', max_length=255, verbose_name='来源url')),
                ('person', models.CharField(help_text='评论用户', max_length=30, verbose_name='评论用户')),
                ('desc', models.CharField(help_text='内容', max_length=500, verbose_name='内容')),
                ('likes', models.IntegerField(default=0, help_text='点赞数', verbose_name='点赞数')),
                ('plat_from', models.CharField(default='PC/网页', help_text='平台', max_length=30, verbose_name='平台')),
                ('reply_person', models.CharField(help_text='被回复用户', max_length=30, verbose_name='被回复用户')),
                ('floor', models.IntegerField(default=0, help_text='楼层', verbose_name='楼层')),
                ('is_main', models.BooleanField(default=True, help_text='是否主楼', verbose_name='是否主楼')),
                ('publish_time', models.DateTimeField(help_text='发布时间', null=True, verbose_name='发布时间')),
            ],
            options={
                'verbose_name': '评论',
                'verbose_name_plural': '评论',
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='用户名', max_length=30, verbose_name='用户名')),
                ('sex', models.CharField(choices=[(0, '保密'), (1, '男'), (2, '女')], default='保密', help_text='性别', max_length=4, verbose_name='性别')),
                ('sign', models.CharField(default='', help_text='个性签名', max_length=200, verbose_name='个性签名')),
                ('uid', models.IntegerField(help_text='用户uid', verbose_name='用户uid')),
                ('level', models.IntegerField(default=0, help_text='用户等级', verbose_name='用户等级')),
                ('birthday', models.DateField(help_text='生日', null=True, verbose_name='用户生日')),
                ('avatar', models.CharField(default='', help_text='用户头像', max_length=255, verbose_name='用户头像')),
                ('attention_nums', models.IntegerField(default=0, help_text='关注数', verbose_name='关注数')),
                ('fence_nums', models.IntegerField(default=0, help_text='粉丝数', verbose_name='粉丝数')),
                ('register_time', models.DateField(help_text='注册日期', verbose_name='注册日期')),
                ('play_game_list', models.CharField(help_text='最近玩过的游戏', max_length=200, verbose_name='最近玩过的游戏')),
                ('member_level', models.CharField(choices=[(0, '普通用户'), (1, '大会员'), (2, '年费大会员')], help_text='会员等级', max_length=6, verbose_name='会员等级')),
                ('subscribe_tags', models.CharField(help_text='标签集', max_length=200, verbose_name='标签集')),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='标签名', max_length=30, verbose_name='标签名')),
                ('likes', models.IntegerField(default=0, help_text='标签关注数', verbose_name='标签关注数')),
                ('publish_nums', models.IntegerField(default=0, help_text='视频数', verbose_name='视频数')),
            ],
            options={
                'verbose_name': '标签',
                'verbose_name_plural': '标签',
            },
        ),
        migrations.CreateModel(
            name='VideoOrArticle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.CharField(help_text='up主', max_length=30, verbose_name='up主')),
                ('title', models.CharField(help_text='标题', max_length=30, verbose_name='标题')),
                ('desc', models.TextField(help_text='描述', verbose_name='描述')),
                ('url', models.CharField(help_text='链接', max_length=255, verbose_name='链接地址')),
                ('play_nums', models.IntegerField(default=0, help_text='播放数', verbose_name='播放数')),
                ('danmu_nums', models.IntegerField(default=0, help_text='弹幕数', verbose_name='弹幕数')),
                ('comments', models.IntegerField(default=0, help_text='评论数', verbose_name='评论数')),
                ('coins', models.IntegerField(default=0, help_text='硬币数', verbose_name='硬币数')),
                ('collections', models.IntegerField(default=0, help_text='收藏数', verbose_name='收藏数')),
                ('likes', models.IntegerField(default=0, help_text='点赞数', verbose_name='点赞数')),
                ('shares', models.IntegerField(default=0, help_text='分享数', verbose_name='分享数')),
                ('publish_time', models.DateTimeField(help_text='发布日期', verbose_name='发布日期')),
                ('tags', models.CharField(help_text='标签集', max_length=200, verbose_name='标签集')),
                ('category', models.CharField(help_text='分类集', max_length=50, verbose_name='分类集')),
            ],
            options={
                'verbose_name': '视频或文章',
                'verbose_name_plural': '视频或文章',
            },
        ),
    ]
