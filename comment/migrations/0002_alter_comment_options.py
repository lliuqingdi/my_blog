# Generated by Django 4.2 on 2024-08-27 14:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comment', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'verbose_name': '评论', 'verbose_name_plural': '评论管理'},
        ),
    ]
