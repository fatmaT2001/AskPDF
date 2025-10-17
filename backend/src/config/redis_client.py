import json
import redis.asyncio as redis
from .settings import get_settings
from .redis_scheme import RedisMessageSchema, RedisMetaSessionSchema
from datetime import datetime

class RedisClient:
    def __init__(self):
        redis_path=f"redis://:{get_settings().REDIS_PASSWORD}@localhost:{get_settings().REDIS_PORT}/0"
        self.client = redis.from_url(redis_path, decode_responses=True)

    def _meta_key(self, user_id: int) -> str:
        return f"session:{user_id}"

    def _list_key(self, user_id: int) -> str:
        return f"session:{user_id}:messages"

    async def create_session(self, session_data: RedisMetaSessionSchema) -> None:
        key = self._meta_key(session_data.user_id)
        await self.client.set(key, session_data.model_dump_json())

    async def get_session(self, user_id: int) -> RedisMetaSessionSchema | None:
        key = self._meta_key(user_id)
        data = await self.client.get(key)
        return RedisMetaSessionSchema.model_validate_json(data) if data else None

    async def append_message(self, user_id: int, msg: RedisMessageSchema) -> None:
        list_key = self._list_key(user_id)
        meta_key = self._meta_key(user_id)
        # 1) append to LIST (fast)
        await self.client.rpush(list_key, msg.model_dump_json())

    async def get_messages(self, user_id: int, limit: int = 50) -> list[RedisMessageSchema]:
        raw = await self.client.lrange(self._list_key(user_id), -limit, -1)
        return [RedisMessageSchema.model_validate_json(x) for x in raw]
