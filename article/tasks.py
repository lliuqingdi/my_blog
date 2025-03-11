from celery import shared_task
from django_redis import get_redis_connection
import logging

logger = logging.getLogger(__name__)


@shared_task
def clean_inactive_searches():
    redis_conn = get_redis_connection("default")
    deleted_count = 0

    cursor = '0'
    while True:
        cursor, keys = redis_conn.scan(
            cursor=cursor,
            match='weekly_search_count:*',
            count=1000  # 每批处理1000个键
        )

        # 批量获取计数器值
        pipeline = redis_conn.pipeline()
        for key in keys:
            pipeline.get(key)
        counts = pipeline.execute()

        # 处理符合条件的用户
        to_delete = []
        for key, count in zip(keys, counts):
            try:
                if int(count or 0) < 3:
                    user_id = key.decode().split(":")[1]
                    history_key = f"search_history:{user_id}"

                    # 检查 zset 是否为空
                    if redis_conn.exists(history_key):
                        if redis_conn.zcard(history_key) == 0:
                            to_delete.append(history_key)

                    to_delete.append(key)  # 删除计数器
            except Exception as e:
                logger.error(f"Error processing key {key}: {str(e)}")

        # 批量删除
        if to_delete:
            redis_conn.delete(*to_delete)
            deleted_count += len(to_delete) // 2

        if cursor == '0':
            break

    logger.info(f"Deleted {deleted_count} inactive search records")
    return deleted_count
