# Generated by Django 2.0.3 on 2018-08-13 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bili', '0008_article_img_box'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='url',
            field=models.CharField(help_text='链接', max_length=255, unique=True, verbose_name='链接地址'),
        ),
    ]