from celery import shared_task
from celery.utils.log import get_task_logger
from celery.exceptions import Retry
import random
from django_redis import get_redis_connection
from datetime import datetime, timedelta  # 导入 datetime 和 timedelta

logger = get_task_logger(__name__)

SEARCH_HISTORY_KEY_PATTERN = "search_history:*"
POPULAR_SEARCH_CACHE_KEY = "popular_searches"  # 定义热门搜索缓存的 Redis 键


@shared_task(bind=True)  # bind=True 使任务可以访问 self
def daily_redis_maintenance(self):
    """每日维护任务"""
    conn = get_redis_connection("default")
    cursor = '0'
    total_processed = 0

    while cursor != 0:
        cursor, keys = conn.scan(
            cursor=cursor,
            match=SEARCH_HISTORY_KEY_PATTERN,
            count=100
        )

        for key in keys:
            try:
                if conn.ttl(key) < 60 * 60 * 24 * 3:  # 剩余时间小于3天
                    expire_seconds = random.randint(604800, 1209600)  # 7-14天
                    conn.expire(key, expire_seconds)
                    total_processed += 1
            except Exception as e:
                logger.error(f"处理键 {key} 失败: {str(e)}")

    logger.info(f"已更新 {total_processed} 个键的过期时间")


@shared_task(bind=True)
def weekly_cache_update(self):
    """每周缓存更新"""
    conn = get_redis_connection("default")

    current_week = datetime.now().isocalendar()[1]
    last_run_week = conn.get("cache_update_week") or 0

    if current_week != last_run_week:
        try:
            # 执行实际的缓存更新逻辑
            logger.info("开始每周缓存更新...")

            # 示例：更新热门搜索缓存
            update_popular_searches()

            conn.set("cache_update_week", current_week)
            logger.info("每周缓存更新完成")
        except Exception as e:
            logger.error(f"每周缓存更新失败: {str(e)}")
            raise self.retry(exc=e, countdown=60)  # 使用 retry 进行重试


def update_popular_searches():
    """更新热门搜索缓存（示例）"""
    conn = get_redis_connection("default")

    # 获取过去一周内所有搜索记录
    one_week_ago = datetime.now() - timedelta(weeks=1)
    keys = conn.keys(SEARCH_HISTORY_KEY_PATTERN)
    search_counts = {}

    for key in keys:
        try:
            # 获取搜索历史记录的所有项，假设记录时间作为排序依据
            history = conn.lrange(key, 0, -1)

            # 统计搜索词出现的次数
            for keyword in history:
                keyword = keyword.decode('utf-8')  # 解码为字符串
                search_counts[keyword] = search_counts.get(keyword, 0) + 1
        except Exception as e:
            logger.error(f"处理键 {key} 时发生错误: {str(e)}")

    # 按照搜索次数排序并选取最热门的搜索词
    sorted_searches = sorted(search_counts.items(), key=lambda item: item[1], reverse=True)

    # 取前 10 个最热门搜索词
    top_searches = [search[0] for search in sorted_searches[:10]]

    # 更新缓存
    conn.set(POPULAR_SEARCH_CACHE_KEY, top_searches)
    logger.info(f"更新热门搜索缓存: {top_searches}")
