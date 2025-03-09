from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_blog.settings")
app = Celery('my_blog')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.timezone = 'Asia/Shanghai'  # 设置上海时区
app.conf.broker_connection_retry_on_startup = True
# 定时任务配置
app.conf.beat_schedule = {
    'clean-inactive-searches': {
        'task': 'app.tasks.clean_inactive_searches',
        'schedule': crontab(
            hour=8,
            minute=0,
            day_of_week=1  # 周一
        ),
        'options': {'queue': 'periodic'}
    },
}