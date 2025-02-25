from django_redis import get_redis_connection


def add_search_history(user_id, keyword):
    """
    添加搜索记录到 Redis
    :param user_id: 用户 ID（如果未登录，可以使用 'anonymous'）
    :param keyword: 搜索关键词
    """
    redis_conn = get_redis_connection("default")
    key = f"search_history:{user_id}"

    # 开始事务
    pipe = redis_conn.pipeline()

    # 如果关键词已存在，先删除旧的记录
    pipe.lrem(key, 0, keyword)

    # 将关键词添加到列表的最前面
    pipe.lpush(key, keyword)

    # 只保留最近的 10 条记录
    pipe.ltrim(key, 0, 9)

    # 提交事务
    pipe.execute()


# def add_search_history(user_id, keyword):
#     """
#     添加搜索记录到 Redis，使用 Lua 脚本来确保并发安全
#     :param user_id: 用户 ID（如果未登录，可以使用 'anonymous'）
#     :param keyword: 搜索关键词
#     """
#     redis_conn = get_redis_connection("default")
#     key = f"search_history:{user_id}"
#
#     lua_script = """
#     -- 删除旧的记录
#     redis.call('lrem', KEYS[1], 0, ARGV[1])
#     -- 将新的记录添加到列表最前面
#     redis.call('lpush', KEYS[1], ARGV[1])
#     -- 保留最多 10 条记录
#     redis.call('ltrim', KEYS[1], 0, 9)
#     """
#
#     redis_conn.eval(lua_script, 1, key, keyword)


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
