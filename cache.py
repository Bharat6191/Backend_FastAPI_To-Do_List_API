import redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def init_cache():
    FastAPICache.init(RedisBackend(redis_client), prefix="todo_cache") # type: ignore