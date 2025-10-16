from pydantic_settings import BaseSettings


class Settings(BaseSettings): 

    USER: str
    PASSWORD: str
    HOST: str
    PORT: int
    DBNAME: str

    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str
    PINECONE_EMBEDDING_MODEL: str
    PINECONE_RERANKING_MODEL: str
    PINECONE_HOST_URL: str

    GENERATION_MODEL_PROVIDER: str
    GROQ_API_KEY: str
    OPEN_ROUTER_API_KEY: str
    LITELLM_BASE_URL: str
    LITELLM_BASE_MODEL: str
    LITELLM_MAP_REDUCE_MODEL: str


    REDIS_PASSWORD: str
    REDIS_PORT: int

    class Config:
        env_file = ".env"



def get_settings():
    return Settings()
