from django_redis import get_redis_connection


def add_search_history(user_id, keyword):
    """
    添加搜索记录到 Redis
    :param user_id: 用户 ID（如果未登录，可以使用 'anonymous'）
    :param keyword: 搜索关键词
    """
    redis_conn = get_redis_connection("default")
    key = f"search_history:{user_id}"

    # 如果关键词已存在，先删除旧的记录
    redis_conn.lrem(key, 0, keyword)

    # 将关键词添加到列表的最前面
    redis_conn.lpush(key, keyword)

    # 只保留最近的 10 条记录
    redis_conn.ltrim(key, 0, 9)


def get_search_history(user_id):
    """
    获取用户的搜索记录
    :param user_id: 用户 ID（如果未登录，可以使用 'anonymous'）
    :return: 搜索记录列表
    """
    redis_conn = get_redis_connection("default")
    key = f"search_history:{user_id}"
    # 获取最近的 10 条记录
    return redis_conn.lrange(key, 0, -1)
