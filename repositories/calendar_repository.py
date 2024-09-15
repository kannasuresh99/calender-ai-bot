from db.couchbase_client import get_bucket
from db.redis_client import get_redis
from models.calendar_event import CalendarEvent

class CalendarRepository:
    def __init__(self):
        self.bucket = get_bucket()
        self.redis = get_redis()

    async def get_events(self, user_id: str):
        cache_key = f"events:{user_id}"
        cached_events = await self.redis.get(cache_key)
        if cached_events:
            return [CalendarEvent.parse_raw(event) for event in cached_events]

        collection = self.bucket.collection("events")
        query = f"SELECT * FROM events WHERE user_id = $1"
        result = await collection.query(query, user_id)
        events = [CalendarEvent(**row) for row in result]

        await self.redis.set(cache_key, [event.json() for event in events], ex=3600)  # Cache for 1 hour
        return events

    async def add_event(self, event: CalendarEvent):
        collection = self.bucket.collection("events")
        await collection.insert(event.id, event.dict())
        await self.invalidate_cache(event.user_id)

    async def update_event(self, event: CalendarEvent):
        collection = self.bucket.collection("events")
        await collection.replace(event.id, event.dict())
        await self.invalidate_cache(event.user_id)

    async def delete_event(self, event_id: str, user_id: str):
        collection = self.bucket.collection("events")
        await collection.remove(event_id)
        await self.invalidate_cache(user_id)

    async def invalidate_cache(self, user_id: str):
        cache_key = f"events:{user_id}"
        await self.redis.delete(cache_key)