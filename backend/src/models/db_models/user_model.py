from .base_model import BaseModel
from ..db_schemes import User,Chat,PDF
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

class UserModel(BaseModel):
    def __init__(self):
        super().__init__()

    async def get_user_by_id(self, user_id: int):
        async with self.db_client() as session:
            result = await session.get(User, user_id)
            return result
        
    async def create_user(self, user_data: User):
        async with self.db_client() as session:
            session.add(user_data)
            await session.commit()
            await session.refresh(user_data)
            return user_data
        
    async def delete_user(self, user_id: int):
        async with self.db_client() as session:
            user = await session.get(User, user_id)
            if user:
                await session.delete(user)
                await session.commit()
                return True
            return False
    

    async def get_user_chats(self,user_id:int)->list[Chat]|None:
        async with self.db_client() as session:
            result = await session.execute(
                select(User)
                .options(selectinload(User.chats))
                .where(User.id == user_id)
            )
            user = result.scalars().one_or_none()
            if user is None:
                return []
            return user.chats

    async def get_user_pdfs(self,user_id:int)->list[PDF]|None:
        async with self.db_client() as session:
            result = await session.execute(
                select(User)   
                .options(selectinload(User.pdfs))
                .where(User.id == user_id)
            )
            user = result.scalars().one_or_none()
            if user is None:
                return []
            return user.pdfs

    async def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        async with self.db_client() as session:
            result = await session.execute(
                select(User).offset(skip).limit(limit)
            )
            return result.scalars().all()