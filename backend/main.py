from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.config import get_db_client , RedisClient
from src.models import db_schemes  
from src.config.database import SQLAlchemyBase, db_engine
from src.routes import user_router, pdf_router, chat_router
from src.stores.vectordb.vectordb_interface import VectorDBInterface
from src.stores.vectordb.vectordb_factory import VectorDBFactory, VectorDBType

async def create_database_tables():
    async with db_engine.begin() as conn:
        await conn.run_sync(SQLAlchemyBase.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code here

    try:
        await create_database_tables()
    except Exception as e:
        print(f"Error creating database tables: {e}")

    # Initialize Redis client
    try:
        redis_client = RedisClient()
        await redis_client.client.ping()
        app.state.redis_client = redis_client
    except Exception as e:
        print(f"Error initializing Redis client: {e}")


    # Initialize  vector DB client
    try:
        vector_db_client: VectorDBInterface = VectorDBFactory().create_vectordb(VectorDBType.PINECONE.value)
        await vector_db_client.connect()
        app.state.vector_db_client = vector_db_client
    except Exception as e:
        print(f"Error initializing vector database client: {e}")
    yield
    # Shutdown code here
    await app.state.db_client.close_all()
    await app.state.redis_client.client.close()
    await app.state.vector_db_client.disconnect()



app=FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router)
app.include_router(pdf_router)
app.include_router(chat_router)