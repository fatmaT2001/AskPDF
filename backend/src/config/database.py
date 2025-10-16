from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from .settings import get_settings

db_path=f"postgresql+asyncpg://{get_settings().USER}:{get_settings().PASSWORD}@{get_settings().HOST}:{get_settings().PORT}/{get_settings().DBNAME}"

db_engine = create_async_engine(db_path)
db_client = sessionmaker(db_engine,class_=AsyncSession, expire_on_commit=False)
SQLAlchemyBase = declarative_base()


def get_db_client():
    if not db_client:
        raise Exception("Database client is not initialized")
    return db_client
