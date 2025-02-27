from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_blog.settings')

app = Celery('my_blog',
             broker='redis://192.168.209.101:6379/1',
             backend='redis://192.168.209.101:6379/2')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# 配置时区
app.conf.timezone = 'Asia/Shanghai'

# 配置定时任务
app.conf.beat_schedule = {
    'daily-redis-maintenance': {
        'task': 'your_app.tasks.daily_redis_maintenance',
        'schedule': 3600.0,  # 每小时检查一次
    },
    'weekly-cache-update': {
        'task': 'your_app.tasks.weekly_cache_update',
        'schedule': 604800.0,  # 每周执行一次
    }
}