from pydantic import BaseModel

class CreateUserScheme(BaseModel):
    username: str
