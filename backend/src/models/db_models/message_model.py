from .base_model import BaseModel
from ..db_schemes import Chat as ChatScheme
from ..db_schemes import Message as MessageScheme
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

class MessageModel(BaseModel):
    def __init__(self):
        super().__init__()
    
    async def create_message(self, message_data:MessageScheme):
        async with self.db_client() as session:
            session.add(message_data)
            await session.commit()
            await session.refresh(message_data)
            return message_data

    async def get_message_by_id(self, message_id:int):
        async with self.db_client() as session:
            result = await session.get(MessageScheme, message_id)
            return result
    
