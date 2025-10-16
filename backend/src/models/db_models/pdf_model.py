from .base_model import BaseModel
from ..db_schemes import PDF as PDFScheme

class PDFModel(BaseModel):
    def __init__(self):
        super().__init__()
    
    async def save_pdf(self, pdf_data:PDFScheme):
        async with self.db_client() as session:
            session.add(pdf_data)
            await session.commit()
            await session.refresh(pdf_data)
            return pdf_data

    async def get_pdf_by_id(self, pdf_id:int):
        async with self.db_client() as session:
            result = await session.get(PDFScheme, pdf_id)
            return result
    
    async def delete_pdf_by_id(self,pdf_id:int):
        async with self.db_client() as session:
            pdf = await session.get(PDFScheme, pdf_id)
            if pdf:
                await session.delete(pdf)
                await session.commit()
                return True
            return False
        
    async def update_pdf_sumamry(self, pdf_id:int, summary:str):
        async with self.db_client() as session:
            pdf = await session.get(PDFScheme, pdf_id)
            if pdf:
                pdf.summary = summary
                session.add(pdf)
                await session.commit()
                await session.refresh(pdf)
                return pdf
            return None
        

        
        
    