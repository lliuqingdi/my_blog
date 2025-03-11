from django_redis import get_redis_connection
import random
import time


def add_search_history(user_id, keyword):
    """使用 zset 维护搜索记录（增加频次统计）"""
    redis_conn = get_redis_connection("default")
    history_key = f"search_history:{user_id}"
    counter_key = f"weekly_search_count:{user_id}"
    timestamp = time.time()

    lua_script = """
    -- 维护搜索历史有序集合（使用时间戳作为分数）
    redis.call('zrem', KEYS[1], ARGV[1])
    redis.call('zadd', KEYS[1], ARGV[2], ARGV[1])
    redis.call('zremrangebyrank', KEYS[1], 0, -(tonumber(ARGV[3]) + 1))  -- 限制最多10条

    -- 更新周搜索计数器
    redis.call('INCR', KEYS[2])
    local ttl = redis.call('ttl', KEYS[2])
    if ttl < 0 then
        redis.call('expire', KEYS[2], 604800)  -- 首次设置7天过期
    end

    -- 设置历史记录过期时间（如果未设置）
    if redis.call('ttl', KEYS[1]) < 0 then
        redis.call('expire', KEYS[1], 86400)
    end
    """
    redis_conn.eval(lua_script, 2, history_key, counter_key, keyword, timestamp, 10)


def get_search_history(user_id):
    """获取搜索记录（续期带随机扰动）"""
    redis_conn = get_redis_connection("default")
    key = f"search_history:{user_id}"

    # 确保 key 是 zset
    if redis_conn.type(key) != b'zset':
        redis_conn.delete(key)

    pipeline = redis_conn.pipeline()
    pipeline.zrevrange(key, 0, -1)  # 按时间倒序获取所有关键词

    # 续期（7天±2小时）
    new_ttl = 604800 + random.randint(-7200, 7200)
    pipeline.expire(key, new_ttl)

    results, _ = pipeline.execute()
    return results

