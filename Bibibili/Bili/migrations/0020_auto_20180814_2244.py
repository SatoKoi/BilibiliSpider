# Generated by Django 2.0.3 on 2018-08-14 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bili', '0019_auto_20180814_2234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='person',
            field=models.CharField(help_text='评论用户', max_length=30, verbose_name='评论用户'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='sid',
            field=models.CharField(help_text='av号或cv号', max_length=30, null=True, verbose_name='av号或cv号'),
        ),
        migrations.AlterUniqueTogether(
            name='comment',
            unique_together={('sid', 'person')},
        ),
    ]
