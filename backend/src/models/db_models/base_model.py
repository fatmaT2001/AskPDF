
from ...config import get_db_client

class BaseModel:
    def __init__(self):
        self.db_client = get_db_client()