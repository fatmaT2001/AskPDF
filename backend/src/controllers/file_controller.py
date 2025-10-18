
import os
import aiofiles
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import AsyncIterator, List
from src.stores.vectordb.vectordb_interface import VectorDBInterface

class FileController:
    def __init__(self,vectordb_instance: VectorDBInterface):
        self.assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.vectordb = vectordb_instance

    async def save_file_locally(self, file_name:str, file_data):
            #save the file locally
            file_location = os.path.join(self.assets_dir, file_name)
            # Use aiofiles for async file writing
            async with aiofiles.open(file_location, "wb") as buffer:
                # Read file content in chunks for better memory management
                while chunk := await file_data.read(8192):  
                    await buffer.write(chunk)
            return file_location
    

    async def delete_local_file(self, file_name: str):
        # first delete the local file
        file_path = os.path.join(self.assets_dir, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)



    async def _stream_pdf_chunks(self, file_path: str) -> AsyncIterator[str]:
        """
        Single-step async loader + splitter that yields chunks (with page metadata).
        Stream-safe: does not accumulate whole document in memory.
        """
        loader = PyPDFLoader(file_path)
        async for page in loader.alazy_load():
            content = page.page_content
            if isinstance(content, list):
                content = "\n".join(content)
            for text in self.text_splitter.split_text(content):
                yield f" Page Number: {page.metadata.get('page')} \n{text}"

    async def get_pdf_chunks(self, file_path: str) -> List[str]:
        """Convenience wrapper to collect all chunks into a list."""
        return [chunk async for chunk in self._stream_pdf_chunks(file_path)]
    

    async def vector_db_index(self, pdf_id: str, chunks: List[str]):
        """Index the PDF chunks into the vector database."""
        await self.vectordb.index(chunks, pdf_id)
