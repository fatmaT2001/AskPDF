from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from ..models.enums.role import Role

class RedisMetaSessionSchema(BaseModel):
    user_id: int
    chat_id: int
    created_at: datetime
    updated_at: datetime
    summary: Optional[str] = None


class RedisMessageSchema(BaseModel):
    role: Role
    content: str
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
