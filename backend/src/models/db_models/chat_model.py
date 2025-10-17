from .base_model import BaseModel
from ..db_schemes import Chat as ChatScheme
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select


class ChatModel(BaseModel):
    def __init__(self):
        super().__init__()
    
    async def create_chat(self, chat_data:ChatScheme):
        async with self.db_client() as session:
            session.add(chat_data)
            await session.commit()
            await session.refresh(chat_data)
            return chat_data

    async def get_chat_by_id(self, chat_id:int):
        async with self.db_client() as session:
            result = await session.get(ChatScheme, chat_id)
            return result
    
    async def delete_chat_by_id(self,chat_id:int):
        async with self.db_client() as session:
            chat = await session.get(ChatScheme, chat_id)
            if chat:
                await session.delete(chat)
                await session.commit()
                return True
            return False
        
    async def get_chat_history(self, chat_id:int):
        async with self.db_client() as session:
            chat = await session.execute(
                select(ChatScheme).options(selectinload(ChatScheme.messages)).where(ChatScheme.id == chat_id)
            )
            if chat:
                return chat.messages
            return []


    async def update_chat_summary(self, chat_id:int, summary:str):
        async with self.db_client() as session:
            chat = await session.get(ChatScheme, chat_id)
            if chat:
                chat.summary = summary
                session.add(chat)
                await session.commit()
                await session.refresh(chat)
                return chat
            return None