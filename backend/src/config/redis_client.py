import asyncio
import redis.asyncio as redis
from .settings import get_settings
from typing import Optional
from pydantic import BaseModel
from typing import List, Dict, Any
import json

class RedisSessionSchema(BaseModel):
    user_id: int
    chat_id: int
    session_data: dict
    created_at: str
    updated_at: str
    summary: Optional[str] = None



class RedisClient:
    def __init__(self):
        redis_path=f"redis://:{get_settings().REDIS_PASSWORD}@localhost:{get_settings().REDIS_PORT}/0"
        self.client = redis.from_url(redis_path, decode_responses=True)

    async def create_session(self, session: RedisSessionSchema) -> None:
        key = f"session:{session.user_id}"
        await self.client.set(key, session.model_dump_json())

    async def get_session(self, user_id: int) -> Optional[RedisSessionSchema]:
        key = f"session:{user_id}"
        raw = await self.client.get(key)
        if not raw:
            return None
        return RedisSessionSchema.model_validate_json(raw)
    
    async def append_message(self, user_id: int, role: str, content: str) -> None:
        """Append a chat message to the user's session."""
        key = f"session:{user_id}:messages"
        message = {"role": role, "content": content}
        # Convert to JSON for clean storage
        await self.client.rpush(key, json.dumps(message))

    async def get_messages(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get the N most recent messages."""
        key = f"session:{user_id}:messages"
        raw_messages = await self.client.lrange(key, -limit, -1)
        return [json.loads(m) for m in raw_messages]
