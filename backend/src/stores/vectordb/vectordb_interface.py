from abc import ABC, abstractmethod


class VectorDBInterface(ABC):
    """Abstract base class for vector database interfaces."""
    @abstractmethod
    def connect(self):
        """Connect to the vector database."""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from the vector database."""
        pass

    @abstractmethod
    def index(self, chunks: list, pdf_id: str):
        """Index the given chunks into the database."""
        pass


    @abstractmethod
    def search(self,user_query: str, top_k: int,pdf_id: str):
        """Query the database for similar vectors."""
        pass

    @abstractmethod
    def delete(self, pdf_id: str):
        """Delete all associated records of a specific PDF from the database by PDF id."""
        pass

    