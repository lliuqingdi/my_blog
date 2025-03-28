# Generated by Django 4.2 on 2025-03-28 02:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0002_alter_profile_options_alter_profile_avatar_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='following',
            field=models.ManyToManyField(blank=True, related_name='followers', to='userprofile.profile', verbose_name='关注关系'),
        ),
    ]
