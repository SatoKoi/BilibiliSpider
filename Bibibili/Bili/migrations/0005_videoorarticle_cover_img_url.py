# Generated by Django 2.0.3 on 2018-08-11 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bili', '0004_videoorarticle_is_video_or_article'),
    ]

    operations = [
        migrations.AddField(
            model_name='videoorarticle',
            name='cover_img_url',
            field=models.CharField(help_text='封面图', max_length=255, null=True, verbose_name='封面图'),
        ),
    ]