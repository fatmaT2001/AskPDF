from fastapi import APIRouter
from src.models.db_models import PDFModel, UserModel
from src.models.db_schemes import PDF
from fastapi import UploadFile, File, HTTPException
from typing import List
from src.controllers import FileController
import os
from fastapi import Request
from src.stores.vectordb.vectordb_interface import VectorDBInterface

router = APIRouter(
    tags=["pdfs"],
)

@router.post("/users/{user_id}/pdfs")
async def create_user_pdf(request: Request, user_id: int, pdf: UploadFile = File(...)):
    pdf_model = PDFModel()
    user_model = UserModel()
    vectordb_instance = request.app.state.vector_db_client
    file_controller = FileController(vectordb_instance=vectordb_instance)
    try:
        user = await user_model.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    #save the file locally
    try:
        file_location = await file_controller.save_file_locally(pdf.filename, pdf)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # get pdf chunks to verify it's a valid pdf
    try:
        chunks = await file_controller.get_pdf_chunks(file_location)
        print(f"Extracted {len(chunks)} chunks from the uploaded PDF.")
        if not chunks:
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF or is empty")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # index the pdf chunks into the vector DB
    try:
        await file_controller.vector_db_index(pdf_id=pdf.filename, chunks=chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # save the pdf record in the database
    try:
        pdf_object = PDF(user_id=user_id, filename=pdf.filename, filepath=file_location)
        created_pdf = await pdf_model.save_pdf(pdf_object)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return created_pdf


@router.get("/users/{user_id}/pdfs/{pdf_id}")
async def get_user_pdf(user_id: int, pdf_id: int):
    pdf_model = PDFModel()
    user_model = UserModel()
    try:
        user = await user_model.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    try:
        pdf = await pdf_model.get_pdf_by_id(pdf_id)
        if pdf is None or pdf.user_id != user_id:
            raise HTTPException(status_code=404, detail="PDF not found for this user")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return pdf


@router.delete("/users/{user_id}/pdfs/{pdf_id}")
async def delete_user_pdf(request: Request, user_id: int, pdf_id: int):
    pdf_model = PDFModel()
    user_model = UserModel()
    vectordb_instance: VectorDBInterface = request.app.state.vector_db_client
    try:
        user = await user_model.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    try:
        pdf = await pdf_model.get_pdf_by_id(pdf_id)
        if pdf is None or pdf.user_id != user_id:
            raise HTTPException(status_code=404, detail="PDF not found for this user")
        
        # delete the file locally
        if os.path.exists(pdf.filepath):
            os.remove(pdf.filepath)
        
        deleted = await pdf_model.delete_pdf_by_id(pdf_id)
        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete PDF")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # delete from vector database
    try:
        await vectordb_instance.delete(pdf_id=pdf_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"detail": "PDF deleted successfully"}

