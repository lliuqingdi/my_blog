from django_redis import get_redis_connection

import random


def add_search_history(user_id, keyword):
    """添加搜索记录（增加频次统计）"""
    redis_conn = get_redis_connection("default")
    history_key = f"search_history:{user_id}"
    counter_key = f"weekly_search_count:{user_id}"

    lua_script = """
    -- 维护搜索历史列表
    redis.call('lrem', KEYS[1], 0, ARGV[1])
    redis.call('lpush', KEYS[1], ARGV[1])
    redis.call('ltrim', KEYS[1], 0, 9)

    -- 更新周搜索计数器
    redis.call('INCR', KEYS[2])
    local ttl = redis.call('ttl', KEYS[2])
    if ttl < 0 then
        redis.call('expire', KEYS[2], 604800)  -- 首次设置7天过期
    end

    -- 设置历史列表过期时间（如果未设置）
    if redis.call('ttl', KEYS[1]) < 0 then
        redis.call('expire', KEYS[1], 86400)
    end
    """
    redis_conn.eval(lua_script, 2, history_key, counter_key, keyword)


def get_search_history(user_id):
    """获取搜索记录（续期带随机扰动）"""
    redis_conn = get_redis_connection("default")
    key = f"search_history:{user_id}"

    pipeline = redis_conn.pipeline()
    pipeline.lrange(key, 0, -1)

    # 使用相同策略的随机续期（7天±2小时）
    new_ttl = 604800 + random.randint(-7200, 7200)
    pipeline.expire(key, new_ttl)  # 保持返回结果结构的关键点

    results, _ = pipeline.execute()
    return results

