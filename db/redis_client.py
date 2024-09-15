import aioredis
from config import REDIS_URL

redis = None

async def init_redis():
    global redis
    redis = await aioredis.from_url(REDIS_URL)

def get_redis():
    return redis