from django_redis import get_redis_connection
from .tasks import daily_redis_maintenance
import random


def add_search_history(user_id, keyword):
    """添加搜索记录（异步维护）"""
    redis_conn = get_redis_connection("default")
    key = f"search_history:{user_id}"

    # Lua脚本保持原子性
    lua_script = """
    redis.call('lrem', KEYS[1], 0, ARGV[1])
    redis.call('lpush', KEYS[1], ARGV[1])
    redis.call('ltrim', KEYS[1], 0, 9)
    if redis.call('ttl', KEYS[1]) < 0 then
        redis.call('expire', KEYS[1], 86400)
    end
    """
    redis_conn.eval(lua_script, 1, key, keyword)

    # 触发异步维护检查
    daily_redis_maintenance.apply_async(countdown=10)  # 10秒后触发


def get_search_history(user_id):
    """获取搜索记录（带自动续期）"""
    redis_conn = get_redis_connection("default")
    key = f"search_history:{user_id}"

    pipeline = redis_conn.pipeline()
    pipeline.lrange(key, 0, -1)
    pipeline.expire(key, random.randint(604800, 1209600))
    results, _ = pipeline.execute()

    return results
